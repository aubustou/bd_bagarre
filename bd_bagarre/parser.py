import pathlib
import re

import bd_bagarre.model.books

BOOK_FILE_EXTENSIONS = {
    'cbz', 'cbr', 'zip', 'rar',
    'txt', 'doc', 'odt', 'rtf',
    'pdf',
}


def parse_directory(directory):
    path_directory = pathlib.Path(directory)

    for path in path_directory.iterdir():
        if path.is_dir():
            parse_directory(path)
        elif path.is_file() and path.suffix in BOOK_FILE_EXTENSIONS:
            parse_file(path)


def parse_file(file_path: pathlib.Path):
    return bd_bagarre.model.books.Book(
        file_name=file_path.name,
        format_type=file_path.suffix,
        title=file_path.stem,
    )
