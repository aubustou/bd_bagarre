import logging
from os import PathLike
from typing import Dict, List, Optional
from uuid import uuid4

import xmltodict
from apischema import deserialize
from bd_bagarre.database import with_session
from bd_bagarre.model.authors import Author
from bd_bagarre.model.books import Book, Publisher, BookFile

logger = logging.getLogger(__name__)

LANGUAGE_MAPPER = {
    "fr": "français",
    "eng": "english",
    "de": "Deutsch",
    "es": "español",
}


def get_raw_metadata(book_path: PathLike) -> Optional[Dict]:
    metadata_file = book_path / "metadata.opf"
    if not metadata_file.exists():
        return
    with open(book_path / "metadata.opf", encoding="utf8") as f:
        content = xmltodict.parse(f.read())

    return content.get("package")


def get_files(book_path: PathLike, book: Book) -> List[BookFile]:
    files = []
    for file in book_path.iterdir():
        if file.name not in {"cover.jpg", "metadata.opf"}:
            book_file = BookFile(id=str(uuid4()), path=str(file), book=book.id)
            files.append(book_file)

    return files


def get_language(metadata: Dict) -> List[str]:
    lines = metadata.get("dc:language", [])
    lines = lines if isinstance(lines, list) else [lines]
    return [LANGUAGE_MAPPER.get(x, "unknown") for x in lines]


def get_identifiers(metadata: Dict) -> Dict[str, str]:
    lines = metadata.get("dc:identifier", [])
    lines = lines if isinstance(lines, list) else [lines]
    identifiers = dict()
    for line in lines:
        scheme = line.get("@opf:scheme")
        if scheme not in {"calibre", "uuid"}:
            identifiers[scheme] = line["#text"]

    return identifiers


@with_session
def get_metadata(book_path: PathLike) -> Optional[Book]:
    content = get_raw_metadata(book_path)
    if not content:
        return

    metadata = content.get("metadata")
    from bd_bagarre.database import session

    publisher_line = metadata.get("dc:publisher")
    publisher = None
    if publisher_line:
        publisher = session.query(Publisher).filter_by(name=publisher_line).first()
        if not publisher:
            publisher = Publisher(name=publisher_line)
            session.add(publisher)
            session.flush()

    authors = []
    lines = metadata.get("dc:creator", [])
    lines = lines if isinstance(lines, list) else [lines]
    for line in lines:
        author = session.query(Author).filter_by(name=line["#text"]).first()
        if not author:
            author = Author(name=line["#text"])
            session.add(author)
        authors.append(author)

    book = deserialize(
        Book,
        dict(
            title=metadata.get("dc:title", ""),
            summary=metadata.get("dc:description", ""),
            cover_path=str(book_path / "cover.jpg"),
        ),
    )
    session.add(book)
    session.flush()

    book.authors = authors
    book.publisher_obj = publisher
    book.language = get_language(metadata)
    book.tags = metadata.get("dc:subject", [])
    book.files = get_files(book_path, book)
    book.identifiers = get_identifiers(metadata)
    session.flush()
    return book
