import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from bd_bagarre.database import Base


@pytest.fixture(scope="function", autouse=True)
def db_session():
    engine = create_engine("sqlite:///database.sqlite3", echo=True)
    yield
    close_all_sessions()
    Base.metadata.drop_all(bind=engine)
