from dataclasses import make_dataclass, MISSING
from inspect import getmembers
from typing import Callable, Optional

from apischema import Undefined
from apischema.conversions import dataclass_model
from sqlalchemy import create_engine, Column
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

session: Optional[scoped_session] = None


def with_session(func: Callable) -> Callable:
    global session

    if session is None:
        session = init_db()
    return func


def init_db() -> scoped_session:
    global session

    engine = create_engine("sqlite:///database.sqlite3", echo=True)
    session = scoped_session(sessionmaker(autocommit=False, bind=engine))
    try:
        session.execute("""SELECT id FROM books LIMIT 1""")
    except OperationalError as e:
        # Assume DB does not exist
        if "no such table" in e.args[0]:
            Base.metadata.create_all(engine)

    return session


def has_default(column: Column) -> bool:
    return (
        column.nullable
        or column.default is not None
        or column.server_default is not None
    )


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    @property
    def python_type(self):
        return str

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


@as_declarative()
class Base:
    def __init_subclass__(cls):
        columns = getmembers(cls, lambda m: isinstance(m, Column))
        if not columns:
            return

        fields = sorted(
            (
                (
                    column.name or field_name,
                    column.type.python_type,
                    Undefined if has_default(column) else MISSING,
                )
                for field_name, column in columns
            ),
            key=lambda x: x[2] != MISSING,
        )
        dataclass_model(cls)(make_dataclass(cls.__name__, fields))
