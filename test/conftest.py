import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from bd_bagarre.database import Base


@pytest.fixture(scope="function", autouse=True)
def db_session():
    engine = create_engine('sqlite:///database.sqlite3',
                           convert_unicode=True,
                           echo=True)
    session = scoped_session(sessionmaker(autocommit=False,
                                          bind=engine))
    yield
    session.close_all()
    Base.metadata.drop_all(bind=engine)
