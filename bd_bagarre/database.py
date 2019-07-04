import json

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


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from bd_bagarre.model.books import Book
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures
    book = Book(title='bagarre', tags={'tags': ['1', '2']})
    db_session.add(book)
    db_session.commit()