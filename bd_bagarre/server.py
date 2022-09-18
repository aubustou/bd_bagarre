from typing import MutableMapping, Optional, Union, cast
from concurrent.futures import ProcessPoolExecutor
import logging
import xmltodict
from zipfile import ZipFile
from uuid import uuid4
from pathlib import Path
from ibm_cloud_sdk_core.authenticators.authenticator import Authenticator
from fastapi import BackgroundTasks
import os
from ibmcloudant.couchdb_session_authenticator import CouchDbSessionAuthenticator

from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.api_exception import ApiException
from fastapi import FastAPI
from pydantic import BaseModel

USERPROFILE_DOC_TYPE = "userprofile"


os.environ.update(
    CLOUDANT_AUTH_TYPE="COUCHDB_SESSION",
    CLOUDANT_URL="http://quirinalis.local:49161",
    CLOUDANT_USERNAME="admin",
    CLOUDANT_PASSWORD="toto",
)


DB_NAME = "bouquins"
COUCHDB_CLIENT: Optional[CloudantV1] = None

LOCAL_PATH = Path(__file__).parent
LIBRARY_PATH = Path("/nfs/quirinalis/Bagarre/Bouquins")
# BEDE_PATH = LIBRARY_PATH / "Japanese"
BEDE_PATH = LIBRARY_PATH / "Bédés"
BOOK_PATH = LIBRARY_PATH / "Bibliotheque"

TO_SCAN_PATHS = [
    # BEDE_PATH,
    BOOK_PATH,
]

RUNNING_SCAN: bool = False

MAX_WORKERS = 8


def get_client(recreate: bool = False) -> CloudantV1:
    global COUCHDB_CLIENT

    if COUCHDB_CLIENT is None or recreate:
        COUCHDB_CLIENT = CloudantV1.new_instance()

    get_db(COUCHDB_CLIENT)
    return COUCHDB_CLIENT


def get_db(client: CloudantV1, db_name: str = DB_NAME) -> str:
    try:
        return client.get_database_information(db=db_name).get_result()
    except ApiException as e:
        if e.code == 404:
            put_database_result = client.put_database(db=db_name).get_result()
            if put_database_result["ok"]:
                logging.info("%s database created.", db_name)
                return client.get_database_information(db=db_name).get_result()
            else:
                raise
        else:
            raise


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
                executor.submit(create_document_from_comicrack, path, True)
            elif path.name == "metadata.opf":
                executor.submit(create_document_from_calibre, path, True)


def _scan_for_books(folders: list[Path] = TO_SCAN_PATHS):
    global RUNNING_SCAN
    if RUNNING_SCAN:
        return

    RUNNING_SCAN = True
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for folder in folders:
            logging.info("Scanning %s", folder)
            recurse_scan(folder, executor)

            logging.info("Scan %s finished", folder)
    RUNNING_SCAN = False


def create_document_from_calibre(path: Path, recreate_client_connection: bool = False):
    content = xmltodict.parse(path.read_text()).get("package", {})
    id_ = str(uuid4())

    create_document(path, content, id_, recreate_client_connection)


def create_document_from_comicrack(
    path: Path, recreate_client_connection: bool = False
):
    with ZipFile(path) as zipped_file:
        try:
            zipped_file.getinfo("ComicInfo.xml")
        except KeyError:
            # Assume file is missing
            logging.info("File ComicInfo.xml is missing")
            return
        with zipped_file.open("ComicInfo.xml") as info_file:
            content = xmltodict.parse(info_file.read()).get("ComicInfo")
        # front_cover = next((int(x["@Image"]) for x in content.get("Pages", {}).get("Page") if x.get("@Type") == "FrontCover"), None)
        # if front_cover is not None:
        #     names = sorted((x for x in zipped_file.namelist() if x != "ComicInfo.xml"))
        #     with zipped_file.open(names[front_cover]) as cover_file:
        #         front_cover = cover_file.read()
    id_ = "_".join(
        [
            content.get(x, "unknown").replace(" ", "_")
            for x in ["Writer", "Series", "Number", "AlternateNumber"]
        ]
    )
    create_document(path, content, id_, recreate_client_connection)


def create_document(path, content: dict, id_: str, recreate_client_connection: bool):
    client = get_client(recreate=recreate_client_connection)

    try:
        client.get_document(DB_NAME, doc_id=id_)
    except ApiException as e:
        if e.code == 404:
            pass
        else:
            raise
    else:
        logging.info("%s already existing", id_)
        return

    logging.info("Add file")

    if not content:
        return

    book = Document.from_dict(content)

    logging.info("Adding %s", id_)
    book.id = id_
    book.file_path = str(path.relative_to(LIBRARY_PATH))
    # book.front_cover = str(front_cover)

    try:
        client.post_document(db=DB_NAME, document=book)
    except ApiException as e:
        if e.code == 409:
            logging.info("Already existing")
        else:
            raise


logging.basicConfig()
# FastAPI specific code
app = FastAPI()


@app.get("/server")
def read_server_informations() -> str:
    client = get_client()
    server_information = client.get_server_information().get_result()
    return f'Server Version: {server_information["version"]}'


@app.get("/db")
def read_db() -> str:
    client = get_client()
    db_information = get_db(client)
    return db_information


@app.get("/books/{title}", response_model=Book)
def read_book(title: str):
    book = get_book(title)
    return book


@app.get("/scan")
async def scan_for_books(background_tasks: BackgroundTasks) -> str:
    global RUNNING_SCAN
    if RUNNING_SCAN:
        return "Already scanning"

    background_tasks.add_task(_scan_for_books)
    return "Scan launched"
