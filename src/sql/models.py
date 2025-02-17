import datetime
import uuid

from .connect import Base
from sqlalchemy import Column, UUID, String, Integer, DATETIME, TIMESTAMP


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    owner = Column(Integer, nullable=False)
    member = Column(Integer, nullable=True)
    ticket = Column(Integer, nullable=True)


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    member = Column(Integer, nullable=False)
    created = Column(TIMESTAMP(timezone=False), default=datetime.datetime.utcnow, index=True)
