# coding: utf-8
import sqlalchemy
from sqlalchemy.orm import backref, relationship

import bd_bagarre.database


class Author(bd_bagarre.database.Base):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    sorting_name = sqlalchemy.Column(sqlalchemy.String)

    book = relationship('AuthorBookLink', back_populates='author')


class AuthorBookLink(bd_bagarre.database.Base):
    __tablename__ = 'author_book_links'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    book_id = sqlalchemy.Column(sqlalchemy.String,
                             sqlalchemy.ForeignKey('books.id'),
                             nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.String,
                               sqlalchemy.ForeignKey('authors.id'),
                               nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    book = relationship('Book', back_populates='authors')
    author = relationship('Author', back_populates='book')


class Writer(Author):
    books = relationship(
        'AuthorBookLink',
)


# class Penciller(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.penciller == Author.id')
#
#
# class Inker(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.inker == Author.id')
#
#
# class Colorist(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.colorist == Author.id')
#
#
# class Letterer(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.letterer == Author.id')
#
#
# class CoverArtist(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.cover_artist == Author.id')
#
#
# class Editor(Author):
#     books = relationship(
#         'Book',
#         primaryjoin='Book.editor == Author.id')