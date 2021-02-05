from uuid import uuid4

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from bd_bagarre.database import Base
from bd_bagarre.model import Resource


class Author(Base, Resource):
    __tablename__ = "authors"

    name = Column(String, nullable=False)
    sorting_name = Column(String)
    birthdate = Column(DateTime)
    birthplace = Column(String)
    nationality = Column(String)
    biography = Column(String)

    books = relationship(
        "Book", secondary="author_books_association", back_populates="authors"
    )

    def __init__(self, name, sorting_name=None, *args, **kwargs):
        if not sorting_name:
            splitted_name = name.split()
            self.sorting_name = (
                splitted_name[1] + ", " + splitted_name[0]
                if len(splitted_name) > 1
                else name
            )
        self.name = name
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)


class Writer(Author):
    pass


class Penciller(Author):
    pass


class Inker(Author):
    pass


class Colorist(Author):
    pass


class Letterer(Author):
    pass


class CoverArtist(Author):
    pass


class Editor(Author):
    pass
