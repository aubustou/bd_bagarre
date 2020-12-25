import pathlib
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey,  Table,  JSON
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


@dataclass()
class BookFormat:
    format: str
    icon_path: str

    id: UUID = uuid4()
    state = "created"
    creation_date: datetime = datetime.now()
    last_update_date: datetime = None
    deletion_date: datetime = None


class Publisher(Base, Resource):
    __tablename__ = "publishers"

    name = Column(String, nullable=False)
    icon_path = Column(String)


@dataclass()
class Imprint:
    name: str
    icon_path: str

    id: UUID = uuid4()
    state = "created"
    creation_date: datetime = datetime.now()
    last_update_date: datetime = None
    deletion_date: datetime = None


@dataclass()
class AgeRating:
    name: str
    icon_path: str

    id: UUID = uuid4()
    state = "created"
    creation_date: datetime = datetime.now()
    last_update_date: datetime = None
    deletion_date: datetime = None


author_books_association = Table("author_books_association", Base.metadata,
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

    authors = relationship("Author", secondary=author_books_association, back_populates="books")
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
    language = Column(String)
    black_and_white = Column(Boolean)
    proposed_values = Column(Boolean)

    alternate_series: List[str] = field(default_factory=list)
    series_complete = Column(Boolean)

    genre: List[str] = field(default_factory=list)
    tags = Column(JSON)

    characters: List[str] = field(default_factory=list)
    main_character_or_team: List[str] = field(default_factory=list)
    teams: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)

    files = relationship("BookFile")
