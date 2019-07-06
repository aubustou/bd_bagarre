import sqlalchemy
from sqlalchemy.orm import backref, relationship

import bd_bagarre.database


class Author(bd_bagarre.database.Base):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    sorting_name = sqlalchemy.Column(sqlalchemy.String)


class Writer(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.writer == Author.id')


class Penciller(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.penciller == Author.id')


class Inker(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.inker == Author.id')


class Colorist(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.colorist == Author.id')


class Letterer(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.letterer == Author.id')


class CoverArtist(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.cover_artist == Author.id')


class Editor(Author):
    books = relationship(
        'Book',
        primaryjoin='Book.editor == Author.id')