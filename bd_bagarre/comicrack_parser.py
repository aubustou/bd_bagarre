import logging
import re
from pathlib import Path
from typing import Optional, Dict
from zipfile import ZipFile

import xmltodict
from apischema import deserializer

from bd_bagarre.model.books import Book


class ComicRackContent(dict):
    pass


def get_metadata(book_path: Path) -> Dict:
    with ZipFile(book_path) as zipped_file:
        try:
            zipped_file.getinfo("ComicInfo.xml")
        except KeyError:
            # Assume file is missing
            logging.debug("File ComicInfo.xml is missing")
            return {}
        with zipped_file.open("ComicInfo.xml") as f:
            raw: Dict = xmltodict.parse(f.read()).get("ComicInfo")

    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    comicrack_content = ComicRackContent(file_path=book_path)
    comicrack_content.update(
        (pattern.sub("_", key).lower(), value) for key, value in raw.items()
    )
    for key in [
        "characters",
        "locations",
    ]:
        value = comicrack_content.get(key)
        if value:
            comicrack_content[key] = [x.strip() for x in value.split(",")]

    return comicrack_content


@deserializer
def from_comicrack_xml(content: ComicRackContent) -> Book:
    return Book()
