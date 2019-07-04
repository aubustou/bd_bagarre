

import sqlalchemy
import sqlalchemy.dialects.sqlite
from sqlalchemy.orm import backref, relationship

import bd_bagarre.database


class Book(bd_bagarre.database.Base):
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    format_type = sqlalchemy.Column(sqlalchemy.String)
    page_number = sqlalchemy.Column(sqlalchemy.Integer)
    rating = sqlalchemy.Column(sqlalchemy.Integer)
    community_rating = sqlalchemy.Column(sqlalchemy.Integer)
    file_path = sqlalchemy.Column(sqlalchemy.String)  #array
    cover_path = sqlalchemy.Column(sqlalchemy.String)

    title = sqlalchemy.Column(sqlalchemy.String)
    series = sqlalchemy.Column(sqlalchemy.String)
    volume = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime)

    book_format = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    publisher = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    imprint = sqlalchemy.Column(sqlalchemy.String)  #foreignkey

    alternate_series = sqlalchemy.Column(sqlalchemy.String)  #array
    alternate_series_number = sqlalchemy.Column(sqlalchemy.Integer)
    story_arc = sqlalchemy.Column(sqlalchemy.String)
    series_group = sqlalchemy.Column(sqlalchemy.String)
    series_complete = sqlalchemy.Column(sqlalchemy.Boolean)

    writer = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('authors.id'))  #array  #foreignkey
    penciller = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    inker = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    colorist = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    letterer = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    cover_artist = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    editor = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey

    genre = sqlalchemy.Column(sqlalchemy.String)  #array
    tags = sqlalchemy.Column(sqlalchemy.dialects.sqlite.JSON)  #array

    age_rating = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    manga = sqlalchemy.Column(sqlalchemy.String)
    language = sqlalchemy.Column(sqlalchemy.String)
    black_and_white = sqlalchemy.Column(sqlalchemy.Boolean)
    proposed_values = sqlalchemy.Column(sqlalchemy.Boolean)

    summary = sqlalchemy.Column(sqlalchemy.String)
    notes = sqlalchemy.Column(sqlalchemy.String)
    review = sqlalchemy.Column(sqlalchemy.String)
    characters = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    main_character_or_team = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    teams = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    locations = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    scan_information = sqlalchemy.Column(sqlalchemy.String)
    web_url = sqlalchemy.Column(sqlalchemy.String)


class Author(bd_bagarre.database.Base):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    sorting_name = sqlalchemy.Column(sqlalchemy.String)

    books = relationship(
        'Book',
        backref=backref('books',
                        uselist=True,
                        cascade='delete,all'))

