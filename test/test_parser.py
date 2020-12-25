import pathlib

import pytest

import bd_bagarre.calibre_parser
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
