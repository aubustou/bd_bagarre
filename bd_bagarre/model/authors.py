# coding: utf-8
import sqlalchemy
from sqlalchemy.orm import backref, relationship

import bd_bagarre.database


class Author(bd_bagarre.database.Base):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    sorting_name = sqlalchemy.Column(sqlalchemy.String)


class AuthorBookLink(bd_bagarre.database.Base):
    __tablename__ = 'author_book_links'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    book = sqlalchemy.Column(sqlalchemy.String,
                             sqlalchemy.ForeignKey('books.id'),
                             nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String,
                               sqlalchemy.ForeignKey('authors.id'),
                               nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Writer(Author):
    books = relationship(
        'Book',
        secondary='author_book_links',
        primaryjoin="""and_(AuthorBookLink.author == Author.id,
                            AuthorBookLink.role == 'writer')""",
        secondaryjoin='AuthorBookLink.book == Book.id')


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