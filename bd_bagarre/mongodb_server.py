from __future__ import annotations

import logging
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Optional, cast
from uuid import uuid4
from zipfile import BadZipFile

import xmltodict
from fastapi import APIRouter, BackgroundTasks, FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from bd_bagarre.comicrack_parser import ComicInfo
from bd_bagarre.comicrack_parser import get_metadata as get_metadata_from_comicrack

MONGODB_CLIENT: Optional[MongoClient] = None


DB_NAME = "bouquins"

LOCAL_PATH = Path(__file__).parent
LIBRARY_PATH = Path("/quirinalis/Bagarre/Bouquins")
# BEDE_PATH = LIBRARY_PATH / "Bédés"/"Japanese"
BEDE_PATH = LIBRARY_PATH / "Bédés"
# BOOK_PATH = LIBRARY_PATH / "Bibliotheque"

TO_SCAN_PATHS = [
    BEDE_PATH,
    # BOOK_PATH,
]

RUNNING_SCAN: bool = False

SHUTTING_DOWN = False
MAX_WORKERS = 8


def get_client(recreate: bool = False) -> MongoClient:
    global MONGODB_CLIENT

    MONGODB_USER = os.getenv("MONGODB_USER", "bd_bagarre")
    if (MONGODB_PASSWORD := os.getenv("MONGODB_PASSWORD")) is None:
        raise ValueError("MONGODB_PASSWORD is not set")
    if (MONGODB_URL := os.getenv("MONGODB_URL")) is None:
        raise ValueError("MONGODB_URL is not set")

    if MONGODB_CLIENT is None or recreate:
        endpoint = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_URL}/?retryWrites=true&w=majority"
        logging.info("Creating new MongoClient at %s", endpoint)
        MONGODB_CLIENT = MongoClient(endpoint)

    return MONGODB_CLIENT


def get_db(db_name: str = DB_NAME, recreate: bool = False) -> Database:
    client = get_client(recreate)
    logging.info("Getting database %s", db_name)
    return client[db_name]


def get_collection(
    collection_name: str = "books", db_name: str = DB_NAME, recreate: bool = False
) -> Collection:
    """Get a collection of books from MongoClient."""
    db = get_db(db_name, recreate)
    logging.info("Getting collection %s", collection_name)
    return db[collection_name]


class Book(BaseModel):
    title: str
    authors: list[str]


class BandeDessinee(Book):
    format: str


def get_book(title: str) -> Optional[Book]:
    client = get_client()
    try:
        result = client.post_find(
            db=DB_NAME,
            selector={"title": {"$eq": title}},
            fields=["title", "authors"],
            limit=1,
        ).get_result()["docs"]
    except ApiException as e:
        if e.code == 404:
            return None
        else:
            raise
    else:
        if result:
            return cast(Book, result[0])
        else:
            return None


def recurse_scan(folder: Path, executor: ProcessPoolExecutor):
    for path in folder.iterdir():
        if path.is_dir():
            recurse_scan(path, executor)
        elif path.is_file():
            if path.suffix == ".cbz":
                # executor.submit(create_document_from_comicrack, path, True)
                create_document_from_comicrack(path)
            elif path.name == "metadata.opf":
                executor.submit(create_document_from_calibre, path, True)


def _scan_for_books(folders: list[Path] = TO_SCAN_PATHS):
    global RUNNING_SCAN
    if RUNNING_SCAN:
        return

    logging.info("Starting scan for books")

    RUNNING_SCAN = True
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for folder in folders:
            logging.info("Scanning %s", folder)
            recurse_scan(folder, executor)

            logging.info("Scan %s finished", folder)

    logging.info("Creating indexes")
    collection = get_collection()
    collection.create_index("file_path", unique=True)
    RUNNING_SCAN = False


def create_document_from_calibre(path: Path, recreate_client_connection: bool = False):
    content = xmltodict.parse(path.read_text()).get("package", {})
    content["_id"] = str(uuid4())

    create_document(path, content, recreate_client_connection)


def create_document_from_comicrack(
    path: Path, recreate_client_connection: bool = False
):
    try:
        content, _ = get_metadata_from_comicrack(path)
    except BadZipFile:
        logging.error("Bad zip file: %s", path)
        return
    content["_id"] = content["file_path"]
    create_document(path, content, recreate_client_connection)


def create_document(path: Path, content: ComicInfo, recreate_client_connection: bool):
    collection = get_collection(recreate=recreate_client_connection)

    logging.info("Creating document for %s", path)
    try:
        collection.update_one({"path": content["file_path"]}, content, upsert=True)
    except DuplicateKeyError:
        logging.warning("Document %s already exists", path)


# FastAPI specific code
router = APIRouter()


def main():
    logging.basicConfig(level=logging.DEBUG)
    collection = get_collection()

    app = FastAPI()
    app.include_router(router)

    from .feed import router as feed_router

    app.include_router(feed_router)

    return app


@router.get("/server")
def read_server_informations() -> str:
    client = get_client()
    server_information = client.get_server_information().get_result()
    return f'Server Version: {server_information["version"]}\n'


@router.get("/db")
def read_db() -> str:
    client = get_client()
    db_information = get_db(client)
    return db_information


@router.get("/books/{title}", response_model=Book)
def read_book(title: str):
    book = get_book(title)
    return book


@router.get("/scan")
async def scan_for_books(background_tasks: BackgroundTasks) -> str:
    global RUNNING_SCAN
    if RUNNING_SCAN:
        return "Already scanning\n"

    background_tasks.add_task(_scan_for_books)
    return "Scan launched\n"


@router.get("/add")
async def add_book() -> str:
    collection = get_collection()
    content, _ = get_metadata_from_comicrack(
        "/quirinalis/Bagarre/Bouquins/Bédés/English/M/Modern Warfare 2 - Ghost (2010)/Modern Warfare 2 - Ghost #06 - Dead and Gone - (English).cbz"
    )
    collection.insert_one(content)
    logging.info("Added book")
    return "Added\n"
