# coding: utf-8
from sqlalchemy import create_engine
import sqlalchemy.ext.declarative
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///database.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


@sqlalchemy.ext.declarative.as_declarative()
class Base(object):
    query = db_session.query_property()


# noinspection PyArgumentList
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from bd_bagarre.model.books import Book
    from bd_bagarre.model.authors import Author
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures
    writer = Author(name='René Goscinny', sorting_name='Goscinny, René')
    db_session.add(writer)
    db_session.commit()
    book = Book(
        title='bagarre',
        writer=writer.id,
        tags={'tags': ['1', '2']},
    )
    db_session.add(book)
    db_session.commit()