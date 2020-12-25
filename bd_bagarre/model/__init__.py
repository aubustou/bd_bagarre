import enum
from uuid import uuid4

from sqlalchemy import Column, String, Enum, DateTime, func

from bd_bagarre.database import GUID


class ResourceState(enum.Enum):
    created = "created"
    deleting = "deleting"
    deleted = "deleted"


class Resource:
    id = Column(GUID(), primary_key=True, default=str(uuid4()))
    state = Column(Enum(ResourceState), server_default="created")
    creation_date = Column(DateTime, server_default=func.current_timestamp())
    last_update_date = Column(DateTime)
    deletion_date = Column(DateTime)