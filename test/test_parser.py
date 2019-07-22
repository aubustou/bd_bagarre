# coding: utf-8

import csv
import pathlib
import shutil

import bd_bagarre.model.books
import bd_bagarre.parser


def test_parse_calibre_opf(tmp_path):
    return
    shutil.copy(pathlib.Path('./metadata.opf'), tmp_path / 'metadata.opf')

    books = bd_bagarre.parser.parse_directory(tmp_path, [])
    assert books


def test_parse_file():
    return
    for filepath, format, series, number, title in [
        ('Cap Horn T03.cbz', 'cbz', 'Cap Horn', 3, None),
        ('Black OP 6 - Desberg-Labiano.cbz', 'cbz', 'Black OP', 6, 'Desberg-Labiano'),
        ('Cap Horn T03.cbz', 'cbz', 'Cap Horn', 3, None),
        ('Cap Horn T03.cbz', 'cbz', 'Cap Horn', 3, None),
        ('Cap Horn T03.cbz', 'cbz', 'Cap Horn', 3, None),
        ('c:\Documents\Cap Horn T03.cbz', 'cbz', 'Cap Horn', 3, None),
    ]:
        book = bd_bagarre.parser.parse_file(pathlib.Path(filepath))
        assert book.format_type == format
        assert book.series == series
        assert book.number == number
        assert book.title == title
        assert book.file_path == filepath


def test_csv():
    with open('Mes livres.csv', encoding='utf-8') as f:
        content = csv.DictReader(f)
        for row in content:
            print(['{}: {}  '.format(key, value) for key, value in row.items()])
            import pdb; pdb.set_trace()