from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Literal, TypedDict, cast
from zipfile import ZipFile

import magic
import xmltodict


class MandatoryComicInfo(TypedDict):
    file_path: str


class OptionalComicInfo(TypedDict, total=False):
    series: str
    number: str
    volume: str
    title: str
    writer: str
    penciller: str
    inker: str
    colorist: str
    letterer: str
    cover_artist: str
    editor: str
    publisher: str
    imprint: str
    genre: str
    web: str
    characters: str
    teams: str
    locations: str
    synopsis: str
    notes: str
    year: str
    month: str
    day: str
    language_i_s_o: str
    format: str
    page_count: str
    black_and_white: str
    manga: str
    age_rating: str
    age_rating_reason: str
    alternate_series: str
    alternate_number: str
    alternate_count: str
    isbn: str
    barcode: str
    color: str
    trim_size: str
    binding: str
    series_group: str
    series_position: str
    series_index: str


class ComicInfo(MandatoryComicInfo, OptionalComicInfo):
    pass


class ComicRackContent(TypedDict, total=False):
    Series: str
    Number: str
    Volume: str
    Title: str
    Writer: str
    Penciller: str
    Inker: str
    Colorist: str
    Letterer: str
    CoverArtist: str
    Editor: str
    Publisher: str
    Imprint: str
    Genre: str
    Web: str
    Characters: str
    Teams: str
    Locations: str
    Synopsis: str
    Notes: str
    Year: str
    Month: str
    Day: str
    LanguageISO: str
    Format: str
    PageCount: str
    BlackAndWhite: str
    Manga: str
    AgeRating: str
    AgeRatingReason: str
    AlternateSeries: str
    AlternateNumber: str
    AlternateCount: str
    Isbn: str
    Barcode: str
    Color: str
    TrimSize: str
    Binding: str
    SeriesGroup: str
    SeriesPosition: str
    SeriesIndex: str

    Pages: dict[Literal["Page"], list[ComicRackPage]]


MandatoryComicRackPage = TypedDict(
    "MandatoryComicRackPage",
    {
        "@Image": str,
        "@ImageSize": str,
        "@ImageWidth": str,
        "@ImageHeight": str,
    },
)
OptionalComicRackPage = TypedDict(
    "OptionalComicRackPage",
    {"@Type": Literal["FrontCover"]},
    total=False,
)


class ComicRackPage(MandatoryComicRackPage, OptionalComicRackPage):
    pass


SNAKECASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snakecase(value: str) -> str:
    return SNAKECASE_PATTERN.sub("_", value).lower()

def get_metadata(book_path: Path) -> tuple[ComicInfo, bytes]:
    logging.info("Parsing comicrack metadata for %s", book_path)

    # if not magic.from_file(book_path, mime=True).startswith("application/zip"):
    #     logging.warning("Not a zip file: %s", book_path)
    #     return ComicInfo(file_path=str(book_path)), b""

    with ZipFile(book_path) as zipped_file:
        try:
            zipped_file.getinfo("ComicInfo.xml")
        except KeyError:
            # Assume file is missing
            logging.debug("File ComicInfo.xml is missing")
            return ComicInfo(file_path=str(book_path)), b""

        with zipped_file.open("ComicInfo.xml") as f:
            raw = cast(ComicRackContent, xmltodict.parse(f.read()).get("ComicInfo", {}))

        # Get front cover as bytes
        front_page_content = b""
        if pages := raw.pop("Pages", {}).get("Page", []):
            if isinstance(pages, dict):
                pages = [pages]
            logging.debug("Found %d pages", len(pages))

            front_page = next(
                (x for x in pages if x.get("@Type") == "FrontCover"), pages[0]
            )
            front_page_number = front_page["@Image"]
            front_page_path = f"P{front_page_number.zfill(5)}.jpg"
            try:
                zipped_file.getinfo(front_page_path)
            except KeyError:
                logging.debug("File %s is missing", front_page_path)
            else:
                with zipped_file.open(front_page_path) as front_page_img:
                    front_page_content = front_page_img.read()

    # Remove useless keys
    for key in [
        "@xmlns:xsd",
        "@xmlns:xsi",
    ]:
        raw.pop(key, None)

    comicrack_content = ComicInfo(
        file_path=str(book_path),
        **{to_snakecase(key): value for key, value in raw.items()},
    )
    for key in [
        "characters",
        "locations",
    ]:
        if value := comicrack_content.get(key):
            comicrack_content[key] = [x.strip() for x in value.split(",")]

    return comicrack_content, front_page_content
