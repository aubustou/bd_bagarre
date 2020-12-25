import pathlib

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    JSON,
)
from sqlalchemy.orm import relationship

from bd_bagarre.database import Base
from bd_bagarre.model import Resource


class BookFile(Base, Resource):
    __tablename__ = "book_files"

    path = Column(String, nullable=False)
    book = Column(String, ForeignKey("books.id"))

    @property
    def name(self):
        return pathlib.Path(self.path).name

    @property
    def format(self):
        return pathlib.Path(self.path).suffix


class BookFormat(Base, Resource):
    __tablename__ = "book_formats"
    format: str
    icon_path: str


class Publisher(Base, Resource):
    __tablename__ = "publishers"

    name = Column(String, nullable=False)
    icon_path = Column(String)


class Imprint(Base, Resource):
    __tablename__ = "imprints"
    name: str
    icon_path: str


class AgeRating(Base, Resource):
    __tablename__ = "age_ratings"
    name: str
    icon_path: str


author_books_association = Table(
    "author_books_association",
    Base.metadata,
    Column("book", String, ForeignKey("books.id")),
    Column("author", String, ForeignKey("authors.id")),
)


class Book(Base, Resource):
    __tablename__ = "books"

    title = Column(String, nullable=False)
    series = Column(String)
    volume = Column(String)
    number = Column(String)
    publish_date = Column(DateTime)

    authors = relationship(
        "Author", secondary=author_books_association, back_populates="books"
    )
    publisher = Column(String, ForeignKey("publishers.id"))
    publisher_obj = relationship("Publisher", uselist=False)

    format_type = Column(String)
    page_number = Column(Integer)
    rating = Column(Integer)
    community_rating = Column(Integer)
    cover_path = Column(String)

    summary = Column(String)
    notes = Column(String)
    review = Column(String)
    scan_information = Column(String)
    web_url = Column(String)

    book_format = Column(String)

    imprint = Column(String)

    alternate_series_number = Column(Integer)
    story_arc = Column(String)
    series_group = Column(String)

    age_rating = Column(String)
    manga_reading_direction = Column(String)
    language = Column(JSON)
    black_and_white = Column(Boolean)
    proposed_values = Column(Boolean)

    alternate_series = Column(JSON)
    series_complete = Column(Boolean)

    genre = Column(JSON)
    tags = Column(JSON)

    characters = Column(JSON)
    main_character_or_team = Column(JSON)
    teams = Column(JSON)
    locations = Column(JSON)

    identifiers = Column(JSON)

    files = relationship("BookFile")
