from os import PathLike
from typing import Dict, List
from uuid import uuid4

import xmltodict
from apischema import deserialize

from bd_bagarre.database import session
from bd_bagarre.model.authors import Author
from bd_bagarre.model.books import Book, Publisher, BookFile

LANGUAGE_MAPPER = {
    "fr": "français",
    "eng": "english",
    "de": "Deutsch",
    "es": "español",
}


def get_raw_metadata(book_path: PathLike) -> Dict:
    with open(book_path / "metadata.opf") as f:
        content = xmltodict.parse(f.read())

    return content.get('package')


def get_files(book_path: PathLike, book: Book) -> None:
    files = []
    for file in book_path.iterdir():
        if file.name not in {"cover.jpg", "metadata.opf"}:
            book_file = BookFile(id=str(uuid4()), path=str(file), book=book.id)
            files.append(book_file)

    return files


def get_metadata(book_path: PathLike) -> Book:
    content = get_raw_metadata(book_path)

    metadata = content.get("metadata")

    publisher = session.query(Publisher).filter_by(name=metadata.get("dc:publisher")).first()
    if not publisher:
        publisher = Publisher(name=metadata.get("dc:publisher"))
        session.add(publisher)
        session.flush()

    authors = []
    for line in metadata.get("dc:creator", []):
        author = session.query(Author).filter_by(name=line["#text"]).first()
        if not author:
            author = Author(name=line["#text"])
            session.add(author)
            session.flush()
        authors.append(author)

    book = deserialize(Book, dict(
        title=metadata.get("dc:title"),
        summary=metadata.get("dc:description"),
        language=LANGUAGE_MAPPER.get(metadata.get("dc:language"), "unknown"),
        publisher=publisher.id,
        cover_path=str(book_path / "cover.jpg"),
    ))
    session.add(book)
    session.flush()

    book.authors = authors
    book.tags = metadata.get("dc:subject", [])
    book.files = get_files(book_path, book)
    session.flush()
    return book
