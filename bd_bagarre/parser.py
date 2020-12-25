import argparse
import logging

import pathlib
import re

import bd_bagarre.model.books
import bd_bagarre.model.authors
from bd_bagarre.calibre_parser import get_metadata
from bd_bagarre.database import init_db

logger = logging.getLogger(__name__)

BOOK_FILE_EXTENSIONS = {
    "cbz",
    "cbr",
    "zip",
    "rar",
    "txt",
    "doc",
    "odt",
    "rtf",
    "pdf",
}
FILENAME_PATTERNS = [
    r"^(?P<series>.*) T(?P<number>[0-9]*)$",
    r"^(?P<series>.*) - T(?P<number>[0-9]*) - (?P<title>.*)$",
    r"^(?P<series>.*) - (?P<number>[0-9]*) - (?P<title>.*)$",
    r"^(?P<series>.*) (?P<number>[0-9]*)$",
    r"^(?P<series>.*) (?P<number>[0-9]*) - (?P<title>.*)$",
]
FILENAME_COMPILED_PATTERNS = [re.compile(p) for p in FILENAME_PATTERNS]


def parse_file(file_path: pathlib.Path):
    title = file_path.stem
    infos = {"title": title}

    for pattern in FILENAME_COMPILED_PATTERNS:
        match = pattern.match(title)
        if match:
            infos.update(match.groupdict())
            break

    book = bd_bagarre.model.books.Book(format_type=file_path.suffix.strip("."), **infos)
    book.append(bd_bagarre.model.books.BookFile(file_path=str(file_path)))

    return book


def parse_calibre_library() -> None:
    parser = argparse.ArgumentParser(
        prog="Calibre library for BD Bagarre",
        description="Parse a Calibre library directory and add found books",
    )
    parser.add_argument("directory", type=str, help="directory to parse for books")
    parser.add_argument(
        "-n", "--workers", type=int, help="number of workers", default=1
    )
    args = parser.parse_args()

    directory = pathlib.Path(args.directory)
    worker_number = args.workers

    init_db()

    if not directory.exists():
        raise RuntimeError(f"{directory} does not exist")
    if not worker_number:
        raise RuntimeError("Use more than 0 worker")

    for author_dir in directory.iterdir():
        if not author_dir.is_dir():
            continue

        for book_dir in author_dir.iterdir():
            get_metadata(book_dir)


if __name__ == "__main__":
    parse_calibre_library()
