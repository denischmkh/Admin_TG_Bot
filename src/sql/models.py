import datetime
import uuid

from .connect import Base
from sqlalchemy import Column, UUID, String, Integer, DATETIME, TIMESTAMP


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    owner = Column(String, nullable=False)
    member = Column(String, nullable=False)
    ticket = Column(Integer, nullable=False)

class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    member = Column(Integer, nullable=False)
    created = Column(TIMESTAMP(timezone=False), default=datetime.datetime.utcnow, index=True)
