# coding: utf-8

from sqlalchemy import create_engine
import sqlalchemy.ext.declarative
from sqlalchemy.orm import scoped_session, sessionmaker
import pytest

engine = create_engine('sqlite:///database.sqlite3',
                       convert_unicode=True,
                       echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(engine)
    yield Session
    Session.close_all()
    Base.metadata.drop_all(bind=engine)