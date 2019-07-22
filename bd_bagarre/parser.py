# coding utf-8

import csv
import pathlib
import re

import dateutil.parser
import lxml.etree
import lxml.objectify

import bd_bagarre.model.books
import bd_bagarre.model.authors


BOOK_FILE_EXTENSIONS = {
    'cbz', 'cbr', 'zip', 'rar',
    'txt', 'doc', 'odt', 'rtf',
    'pdf',
}
FILENAME_PATTERNS = [
    r'^(?P<series>.*) T(?P<number>[0-9]*)$',
    r'^(?P<series>.*) - T(?P<number>[0-9]*) - (?P<title>.*)$',
    r'^(?P<series>.*) - (?P<number>[0-9]*) - (?P<title>.*)$',
    r'^(?P<series>.*) (?P<number>[0-9]*)$',
    r'^(?P<series>.*) (?P<number>[0-9]*) - (?P<title>.*)$',
]
FILENAME_COMPILED_PATTERNS = [
    re.compile(p) for p in FILENAME_PATTERNS
]


def parse_directory(directory: pathlib.Path, books=None):
    if books is None:
        books = []
    path_directory = pathlib.Path(directory)

    #metadata_file_path = path_directory / 'metadata.opf'
    #if metadata_file_path.exists():
    #    books.append(parse_calibre_metadata(metadata_file_path))
    #    return books

    for path in path_directory.iterdir():
        if path.is_dir():
            books = parse_directory(path, books)
        elif path.is_file():
            if path.suffix in BOOK_FILE_EXTENSIONS:
                books.append(parse_file(path))

    return books


def parse_file(file_path: pathlib.Path):
    title = file_path.stem
    infos = {'title': title}

    import pdb; pdb.set_trace()
    for pattern in FILENAME_COMPILED_PATTERNS:
        match = pattern.match(title)
        if match:
            infos.update(match.groupdict())
            break

    book = bd_bagarre.model.books.Book(
        format_type=file_path.suffix.strip('.'),
        **infos
    )
    book.append(bd_bagarre.model.books.BookFile(file_path=str(file_path)))

    return book


def parse_calibre_metadata(file):
    infos = {
        'file_path': str(file),
        'format_type': file.suffix.strip('.'),
    }

    with open(file, 'rb') as f:
        for _, e in lxml.etree.iterparse(f, encoding='utf-8'):
            tag = lxml.etree.QName(e.tag).localname
            if tag == 'title':
                infos['title'] = e.text
            elif tag == 'publisher':
                infos['publisher'] = e.text
            elif tag == 'description':
                infos['summary'] = e.text
            elif tag == 'language':
                infos['language'] = e.text

    s = """<dc:title>High Performance Spark: Best Practices for Scaling and Optimizing Apache Spark</dc:title>
        <dc:creator opf:file-as="Karau, Holden &amp; Warren, Rachel" opf:role="aut">Holden Karau</dc:creator>
        <dc:creator opf:file-as="Karau, Holden &amp; Warren, Rachel" opf:role="aut">Rachel Warren</dc:creator>
        <dc:contributor opf:file-as="calibre" opf:role="bkp">calibre (2.55.0) [http://calibre-ebook.com]</dc:contributor>
        <dc:date>2017-05-25T23:06:53.568733+00:00</dc:date>
        <dc:identifier opf:scheme="GOOGLE">o0IlDwAAQBAJ</dc:identifier>
        <dc:identifier opf:scheme="ISBN">9781491943151</dc:identifier>
        <dc:language>eng</dc:language>
        <dc:subject>Computers</dc:subject>
        <dc:subject>Data Processing</dc:subject>
        <dc:subject>Databases</dc:subject>
        <dc:subject>Data Warehousing</dc:subject>
        <dc:subject>Enterprise Applications</dc:subject>
        <dc:subject>Business Intelligence Tools</dc:subject>
        <dc:subject>Web</dc:subject>
        <dc:subject>Web Programming</dc:subject>
        <dc:subject>Internet</dc:subject>
        <dc:subject>Application Development</dc:subject>
        <dc:subject>Data Mining</dc:subject>
        <dc:subject>Desktop Applications</dc:subject>
        <dc:subject>General</dc:subject>
        <dc:subject>Programming Languages</dc:subject>
        <dc:subject>Java</dc:subject>
        <dc:subject>Programming</dc:subject>
        <dc:subject>Open Source</dc:subject>
        <meta content="{&quot;Holden Karau&quot;: &quot;&quot;, &quot;Rachel Warren&quot;: &quot;&quot;}" name="calibre:author_link_map"/>
        <meta content="2017-11-27T19:50:30+00:00" name="calibre:timestamp"/>
        <meta content="High Performance Spark: Best Practices for Scaling and Optimizing Apache Spark" name="calibre:title_sort"/>
        <meta content="{&quot;Rangés&quot;: [], &quot;Revues rangées&quot;: []}" name="calibre:user_categories"/>
        <meta name="calibre:user_metadata:#lecteur" content="{&quot;is_category&quot;: true, &quot;#extra#&quot;: null, &quot;kind&quot;: &quot;field&quot;, &quot;is_custom&quot;: true, &quot;is_csp&quot;: false, &quot;colnum&quot;: 1, &quot;column&quot;: &quot;value&quot;, &quot;rec_index&quot;: 23, &quot;search_terms&quot;: [&quot;#lecteur&quot;], &quot;link_column&quot;: &quot;value&quot;, &quot;is_multiple2&quot;: {}, &quot;is_multiple&quot;: null, &quot;datatype&quot;: &quot;text&quot;, &quot;#value#&quot;: null, &quot;category_sort&quot;: &quot;value&quot;, &quot;table&quot;: &quot;custom_column_1&quot;, &quot;is_editable&quot;: true, &quot;label&quot;: &quot;lecteur&quot;, &quot;display&quot;: {&quot;use_decorations&quot;: 0}, &quot;name&quot;: &quot;Lecteur&quot;}"/>
        <meta name="calibre:user_metadata:#formats" content="{&quot;is_category&quot;: false, &quot;#extra#&quot;: null, &quot;kind&quot;: &quot;field&quot;, &quot;is_custom&quot;: true, &quot;is_csp&quot;: false, &quot;colnum&quot;: 2, &quot;column&quot;: &quot;value&quot;, &quot;rec_index&quot;: 22, &quot;search_terms&quot;: [&quot;#formats&quot;], &quot;link_column&quot;: &quot;value&quot;, &quot;is_multiple2&quot;: {}, &quot;is_multiple&quot;: null, &quot;datatype&quot;: &quot;composite&quot;, &quot;#value#&quot;: &quot;EPUB&quot;, &quot;category_sort&quot;: &quot;value&quot;, &quot;table&quot;: &quot;custom_column_2&quot;, &quot;is_editable&quot;: true, &quot;label&quot;: &quot;formats&quot;, &quot;display&quot;: {&quot;contains_html&quot;: false, &quot;composite_template&quot;: &quot;{formats}&quot;, &quot;make_category&quot;: false, &quot;use_decorations&quot;: 0, &quot;composite_sort&quot;: &quot;text&quot;}, &quot;name&quot;: &quot;Formats&quot;}"/>
    </metadata>
    <guide>
        <reference href="cover.jpg" title="Couverture" type="cover"/>
    </guide>"""
    return bd_bagarre.model.books.Book(
        file_path=str(file_path),
        format_type=file_path.suffix.strip('.'),
        **infos
    )


def parse_calibre_csv(db_session, file):
    with open(file, encoding='utf-8-sig') as f:
        content = csv.DictReader(f)

        for line in content:
            cover = line['cover']
            title = line['title']

            book = bd_bagarre.model.books.Book(
                title=title,
                series=line['series'],
                number=line['series_index'],
                tags=line['tags'],
                summary=line['comments'],
                language=line['languages'],
                cover_path=cover,
                rating=line['rating'],
                publish_date=dateutil.parser.parse(line['pubdate']),
            )
            db_session.add(book)
            db_session.commit()
            authors = line['authors'].split('&')

            for author in authors:
                link = bd_bagarre.model.authors.AuthorBookLink()
                obj = bd_bagarre.model.authors.Author.query.filter_by(
                    name=author).first()
                if not obj:
                    obj = bd_bagarre.model.authors.Author(name=author.strip())
                    db_session.add(obj)
                link.author = obj
                db_session.add(link)
                book.authors.append(link)

            publisher = line['publisher']
            if publisher:
                publisher_obj = bd_bagarre.model.books.Publisher.query.filter_by(
                    name=publisher).first()
                if not publisher_obj:
                    publisher_obj = bd_bagarre.model.books.Publisher(
                        name=publisher)
                    db_session.add(publisher_obj)
                    db_session.commit()
                book._publisher = publisher_obj.id

            file_folder = pathlib.Path(cover).parent if cover else None
            if file_folder:
                for format in line['formats'].split(','):

                    file_path = next(file_folder.glob('*.' + format.strip()))
                    if file_path.exists():
                        file_path_obj = bd_bagarre.model.books.BookFile(
                            name=format,
                            path=str(file_path),
                        )
                        db_session.add(file_path_obj)
                        book.files.append(file_path_obj)

            db_session.commit()