import pathlib
from zipfile import ZipFile

import pytest

import bd_bagarre.calibre_parser
from bd_bagarre.comicrack_parser import get_metadata
from bd_bagarre.model.authors import Author
from bd_bagarre.model.books import Publisher, BookFile

calibre_opf_file_content = """<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:identifier opf:scheme="calibre" id="calibre_id">12745</dc:identifier>
        <dc:identifier opf:scheme="uuid" id="uuid_id">58607c66-b3f4-4615-b70e-ea79e454ffd4</dc:identifier>
        <dc:title>{title}</dc:title>
        <dc:creator opf:file-as="Karau, Holden &amp; Warren, Rachel" opf:role="aut">{author_1}</dc:creator>
        <dc:creator opf:file-as="Karau, Holden &amp; Warren, Rachel" opf:role="aut">{author_2}</dc:creator>
        <dc:contributor opf:file-as="calibre" opf:role="bkp">calibre (2.55.0) [http://calibre-ebook.com]</dc:contributor>
        <dc:date>2017-05-25T23:06:53.568733+00:00</dc:date>
        <dc:description>{summary}</dc:description>
        <dc:publisher>{publisher}</dc:publisher>
        <dc:identifier opf:scheme="GOOGLE">{identifier_1}</dc:identifier>
        <dc:identifier opf:scheme="ISBN">{identifier_2}</dc:identifier>
        <dc:language>{language}</dc:language>
        <dc:subject>{tag_1}</dc:subject>
        <dc:subject>{tag_2}</dc:subject>
        <dc:subject>{tag_3}</dc:subject>
        <meta content="2017-11-27T19:50:30+00:00" name="calibre:timestamp"/>
        <meta content="High Performance Spark: Best Practices for Scaling and Optimizing Apache Spark" name="calibre:title_sort"/>
        </metadata>
    <guide>
        <reference href="cover.jpg" title="Couverture" type="cover"/>
    </guide>
</package>
"""


comicrack_comicinfo_xml_content = """<?xml version="1.0"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Series>{series}</Series>
  <Number>{number}</Number>
  <Summary>{summary}</Summary>
  <Notes>{notes}</Notes>
  <Year>{year}</Year>
  <Month>{month}</Month>
  <Writer>{writer}</Writer>
  <Penciller>{penciller}</Penciller>
  <Inker>{inker}</Inker>
  <Colorist>{colorist}</Colorist>
  <Letterer>{letterer}</Letterer>
  <CoverArtist>{cover_artist}</CoverArtist>
  <Editor>{editor}</Editor>
  <Publisher>{publisher}</Publisher>
  <Web>{web}</Web>
  <PageCount>40</PageCount>
  <Characters>{characters}</Characters>
  <Locations>{locations}</Locations>
  <Pages>
    <Page Image="0" ImageSize="104082" ImageWidth="975" ImageHeight="1500" Type="FrontCover" />
    <Page Image="1" ImageSize="214168" ImageWidth="975" ImageHeight="1500" />
    <Page Image="2" ImageSize="258658" ImageWidth="975" ImageHeight="1500" />
    <Page Image="3" ImageSize="188866" ImageWidth="975" ImageHeight="1500" />
    <Page Image="4" ImageSize="215575" ImageWidth="975" ImageHeight="1500" />
    <Page Image="5" ImageSize="234054" ImageWidth="975" ImageHeight="1500" />
    <Page Image="6" ImageSize="352129" ImageWidth="975" ImageHeight="1500" />
    <Page Image="7" ImageSize="275247" ImageWidth="975" ImageHeight="1500" />
    <Page Image="8" ImageSize="255508" ImageWidth="975" ImageHeight="1500" />
    <Page Image="9" ImageSize="321550" ImageWidth="975" ImageHeight="1500" />
    <Page Image="10" ImageSize="274161" ImageWidth="975" ImageHeight="1500" />
    <Page Image="11" ImageSize="233163" ImageWidth="975" ImageHeight="1500" />
    <Page Image="12" ImageSize="279282" ImageWidth="975" ImageHeight="1500" />
    <Page Image="13" ImageSize="310492" ImageWidth="975" ImageHeight="1500" />
    <Page Image="14" ImageSize="300876" ImageWidth="975" ImageHeight="1500" />
    <Page Image="15" ImageSize="288725" ImageWidth="975" ImageHeight="1500" />
    <Page Image="16" ImageSize="174801" ImageWidth="975" ImageHeight="1500" />
    <Page Image="17" ImageSize="260493" ImageWidth="975" ImageHeight="1500" />
    <Page Image="18" ImageSize="299390" ImageWidth="975" ImageHeight="1500" />
    <Page Image="19" ImageSize="298717" ImageWidth="975" ImageHeight="1500" />
    <Page Image="20" ImageSize="277103" ImageWidth="975" ImageHeight="1500" />
    <Page Image="21" ImageSize="144274" ImageWidth="975" ImageHeight="1500" />
    <Page Image="22" ImageSize="253255" ImageWidth="975" ImageHeight="1500" />
    <Page Image="23" ImageSize="152752" ImageWidth="975" ImageHeight="1500" />
    <Page Image="24" ImageSize="186674" ImageWidth="975" ImageHeight="1500" />
    <Page Image="25" ImageSize="164621" ImageWidth="975" ImageHeight="1500" />
    <Page Image="26" ImageSize="281930" ImageWidth="975" ImageHeight="1500" />
    <Page Image="27" ImageSize="264245" ImageWidth="975" ImageHeight="1500" />
    <Page Image="28" ImageSize="317073" ImageWidth="975" ImageHeight="1500" />
    <Page Image="29" ImageSize="278271" ImageWidth="975" ImageHeight="1500" />
    <Page Image="30" ImageSize="311418" ImageWidth="975" ImageHeight="1500" />
    <Page Image="31" ImageSize="307339" ImageWidth="975" ImageHeight="1500" />
    <Page Image="32" ImageSize="271497" ImageWidth="975" ImageHeight="1500" />
    <Page Image="33" ImageSize="240224" ImageWidth="975" ImageHeight="1500" />
    <Page Image="34" ImageSize="300921" ImageWidth="975" ImageHeight="1500" />
    <Page Image="35" ImageSize="224753" ImageWidth="975" ImageHeight="1500" />
    <Page Image="36" ImageSize="267676" ImageWidth="975" ImageHeight="1500" />
    <Page Image="37" ImageSize="188895" ImageWidth="975" ImageHeight="1500" />
    <Page Image="38" ImageSize="132565" ImageWidth="975" ImageHeight="1500" />
    <Page Image="39" ImageSize="71461" ImageWidth="975" ImageHeight="1500" />
  </Pages>
</ComicInfo>"""


@pytest.fixture
def calibre_files(tmp_path):
    file_path = tmp_path / "metadata.opf"
    book_file_1 = tmp_path / "example.rar"
    book_file_1.touch()
    book_file_2 = tmp_path / "example.jpg"
    book_file_2.touch()

    content = dict(
        title="High Performance Spark: Best Practices for Scaling and Optimizing Apache Spark",
        author_1="Holden Karau",
        author_2="Rachel Warren",
        summary=(
            "Apache Spark is amazing when everything clicks. But if you haven’t seen the performance "
            "improvements you expected, or still don’t feel confident enough to use Spark in production, "
            "this practical book is for you. Authors Holden Karau and Rachel Warren demonstrate performance"
            " optimizations to help your Spark queries run faster and handle larger data sizes, while "
            "using fewer resources.Ideal for software engineers, data engineers, developers, and system "
            "administrators working with large-scale data applications, this book describes techniques "
            "that can reduce data infrastructure costs and developer hours. Not only will you gain a more "
            "comprehensive understanding of Spark, you’ll also learn how to make it sing. With this book, "
            "you’ll explore:How Spark SQL’s new interfaces improve performance over SQL’s RDD data "
            "structure. The choice between data joins in Core Spark and Spark SQLTechniques for getting "
            "the most out of standard RDD transformationsHow to work around performance issues in Spark’s "
            "key/value pair paradigmWriting high-performance Spark code without Scala or the JVMHow to "
            "test for functionality and performance when applying suggested improvementsUsing Spark MLlib "
            "and Spark ML machine learning librariesSpark’s Streaming components and external community "
            "packages"
        ),
        publisher="O'Reilly Media, Inc.",
        language="eng",
        tag_1="Computer",
        tag_2="Web Programming",
        tag_3="Databases",
        book_1=book_file_1,
        book_2=book_file_2,
        identifier_1="o0IlDwAAQBAJ",
        identifier_2="9781491943151",
    )
    with open(file_path, "w", encoding="utf8") as f:
        f.write(calibre_opf_file_content.format(**content))

    return content


@pytest.fixture
def comicrack_file(tmp_path):
    zipped_file_path = tmp_path / "The Old Guard #01.cbz"
    content = {
        "series": "The Old Guard",
        "number": "1",
        "summary": (
            "Eisner-winning writer GREG RUCKA (LAZARUS, BLACK MAGICK, Wonder Woman) and critically acclaimed "
            "artist LEANDRO FERNÁNDEZ (THE DISCIPLINE, Deadpool, Punisher: MAX) team up together to introduce "
            "THE OLD GUARD, the story of old soldiers who never die…and yet cannot seem to fade away. Trapped "
            "in an immortality without explanation, Andromache of Scythia—“Andy”—and her comrades ply their "
            "trade for those who can find—and afford—their services. But in the 21st century, immortality is "
            "a hard secret to keep, and when you live long enough, you learn that there are many fates worse "
            "than death."
        ),
        "notes": "Scraped metadata from ComicVine [CVDB582567].",
        "year": "2017",
        "month": "2",
        "writer": "Greg Rucka",
        "penciller": "Leandro Fernandez",
        "inker": "Leandro Fernandez",
        "colorist": "Daniela Miwa",
        "letterer": "Jodi Wynne",
        "cover_artist": "Leandro Fernandez",
        "editor": "Alejandro Arbona",
        "publisher": "Image",
        "web": "https://comicvine.gamespot.com/the-old-guard-1/4000-582567/",
        "characters": (
            "Andromache of Scythia, Booker, James Copley, Nicolo of Genoa, Nile Freeman, "
            "Yusuf ibn Ibrahim ibn Muhammad ibn al-Kaysani"
        ),
        "locations": "Afghanistan, Barcelona",
    }
    with ZipFile(zipped_file_path, "w") as zipped_file:
        with zipped_file.open("ComicInfo.xml", "w") as f:
            f.write(comicrack_comicinfo_xml_content.format(**content).encode())

    return content, zipped_file_path


@pytest.mark.skip
def test_parse_calibre_opf(tmp_path, calibre_files):
    book = bd_bagarre.calibre_parser.get_metadata(tmp_path)
    for key in [
        "title",
        "summary",
    ]:
        assert getattr(book, key) == calibre_files[key]
    assert book.language == ["english"]

    assert set(book.tags) == {
        calibre_files["tag_1"],
        calibre_files["tag_2"],
        calibre_files["tag_3"],
    }

    assert all(isinstance(x, Author) for x in book.authors)
    assert book.authors[0].name == calibre_files["author_1"]
    assert book.authors[1].name == calibre_files["author_2"]

    assert isinstance(book.publisher_obj, Publisher)
    assert book.publisher_obj.name == calibre_files["publisher"]

    assert len(book.files) == 2
    assert isinstance(book.files[0], BookFile)
    assert book.files[0].path in {
        str(calibre_files["book_1"]),
        str(calibre_files["book_2"]),
    }
    assert book.files[0].name in {
        x.name for x in [calibre_files["book_1"], calibre_files["book_2"]]
    }
    assert book.files[0].format in {
        x.suffix for x in [calibre_files["book_1"], calibre_files["book_2"]]
    }

    assert {value for key, value in book.identifiers.items()} == {
        calibre_files["identifier_1"],
        calibre_files["identifier_2"],
    }


def test_parse_comicrack_xml(tmp_path, comicrack_file):
    content, file_path = comicrack_file
    gotten_content = get_metadata(file_path)
    assert gotten_content["file_path"] == file_path
    for attr in [
        "series",
        "number",
        "summary",
        "notes",
        "year",
        "month",
        "writer",
        "penciller",
        "inker",
        "colorist",
        "letterer",
        "cover_artist",
        "editor",
        "publisher",
        "web",
    ]:
        assert gotten_content[attr] == content[attr]
    for attr in ["characters", "locations"]:
        assert gotten_content[attr] == [x.strip() for x in content[attr].split(",")]


@pytest.mark.skip
def test_parse_file():
    for filepath, format, series, number, title in [
        ("Cap Horn T03.cbz", "cbz", "Cap Horn", 3, None),
        ("Black OP 6 - Desberg-Labiano.cbz", "cbz", "Black OP", 6, "Desberg-Labiano"),
        ("Cap Horn T03.cbz", "cbz", "Cap Horn", 3, None),
        ("Cap Horn T03.cbz", "cbz", "Cap Horn", 3, None),
        ("Cap Horn T03.cbz", "cbz", "Cap Horn", 3, None),
        ("c:\Documents\Cap Horn T03.cbz", "cbz", "Cap Horn", 3, None),
    ]:
        book = bd_bagarre.parser.parse_file(pathlib.Path(filepath))
        assert book.format_type == format
        assert book.series == series
        assert book.number == number
        assert book.title == title
        assert book.file_path == filepath
