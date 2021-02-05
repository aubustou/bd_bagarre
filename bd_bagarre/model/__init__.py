import enum
from uuid import uuid4

from sqlalchemy import Column, Enum, DateTime, func, String


class ResourceState(enum.Enum):
    created = "created"
    deleting = "deleting"
    deleted = "deleted"


def get_uuid() -> str:
    return str(uuid4())


class Resource:
    id = Column(String, primary_key=True, default=get_uuid)
    state = Column(Enum(ResourceState), default="created")
    creation_date = Column(DateTime, default=func.current_timestamp())
    last_update_date = Column(DateTime)
    deletion_date = Column(DateTime)
