import datetime
import logging

from src.sql.models import Chat, Ticket
from src.sql.connect import get_session
import sqlalchemy as _sql

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s [%(asctime)s]: %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d/%m/%Y %I:%M:%S',
                    encoding='utf-8')

class DBManager:
    @classmethod
    async def check_ticket_exists(cls, user_id: int) -> Ticket | None:
        async with get_session() as session:
            result = await session.execute(_sql.select(Ticket.member).where(Ticket.member == user_id))
            exist_ticket = result.scalars().first()
            return exist_ticket if exist_ticket else None

    @classmethod
    async def create_ticket(cls, user_id: int) -> str:
        if await cls.check_ticket_exists(user_id):
            return 'Ticket already exists!'
        ticket = Ticket(member=user_id)
        async with get_session() as session:
            session.add(ticket)
            await session.commit()
            logging.info(f'Ticket: {ticket.id} was created successfully')
        return str(ticket.id)

    @classmethod
    async def close_ticket(cls, user_id: int) -> str:
        exists_ticket = await cls.check_ticket_exists(user_id)
        if not exists_ticket:
            return 'Ticket not found!'
        async with get_session() as session:
            await session.execute(_sql.delete(Ticket).where(Ticket.member == user_id))
            await session.commit()
            logging.info(f'Ticket: {exists_ticket} was deleted')
        return str(exists_ticket)
