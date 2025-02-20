import datetime
import logging

from init_bot import bot
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
    async def close_ticket(cls, user_id: int) -> str | None:
        exists_ticket = await cls.check_ticket_exists(user_id)
        if exists_ticket:
            async with get_session() as session:
                await session.execute(_sql.delete(Ticket).where(Ticket.member == user_id))
                await session.commit()
                logging.info(f'Ticket: {exists_ticket} was deleted')
        else:
            exists_chat = await cls.get_chat(user_id)
            if not exists_chat:
                return 'Request invalid'
            await cls.close_chat(exists_chat.owner)
            await cls.create_chat(exists_chat.owner)
            await bot.send_message(chat_id=exists_chat.owner, text='Чат закрыт пользователем')



    @classmethod
    async def check_chat_exists(cls, owner_id: int) -> Chat | None:
        async with get_session() as session:
            result = await session.execute(_sql.select(Chat).where(Chat.owner == owner_id))
            chat = result.scalars().first()
            return chat if chat else None
    @classmethod
    async def create_chat(cls, owner_id: int) -> str:
        exist_chat = await cls.check_chat_exists(owner_id)
        if exist_chat:
            return 'Chat already exists'
        chat = Chat(owner=owner_id,
                    member=None,
                    ticket=None,)
        async with get_session() as session:
            session.add(chat)
            await session.commit()
        return 'Chat created successfully'

    @classmethod
    async def close_chat(cls, owner_id: int) -> str:
        exist_chat = await cls.check_chat_exists(owner_id)
        if not exist_chat:
            return 'Chat not found!'
        async with get_session() as session:
            await session.execute(_sql.delete(Chat).where(Chat.owner == owner_id))
            await session.commit()
        if exist_chat.member:
            await bot.send_message(chat_id=exist_chat.member, text='Чат закрыт❌')
        logging.info(f'Chat was closed by{owner_id}')
        return 'Chat has been closed'

    @classmethod
    async def select_next_ticket(cls, owner_id: int) -> Chat | str:
        exist_chat = await cls.check_chat_exists(owner_id)
        if not exist_chat:
            return 'Chat not found!'
        else:
            if exist_chat.member:
                await bot.send_message(chat_id=exist_chat.member, text='Чат закрыт❌')
        async with get_session() as session:
            result = await session.execute(_sql.select(Ticket))
            tickets = result.scalars().all()
            if not tickets:
                await cls.close_chat(exist_chat.owner)
                await cls.create_chat(exist_chat.owner)
                return 'No tickets!'
            sorted_tickets: list[Ticket] = sorted(tickets, key=lambda ticket: ticket.created)
            oldest_ticket = sorted_tickets[0]
            await session.execute(_sql.update(Chat).where(Chat.owner == owner_id).values(member=oldest_ticket.member, ticket=oldest_ticket.id))
            await session.execute(_sql.delete(Ticket).where(Ticket.id == oldest_ticket.id))
            await session.commit()
            result = await session.execute(_sql.select(Chat).where(Chat.owner == owner_id))
            updated_chat = result.scalars().first()
            return updated_chat

    @classmethod
    async def get_chat(cls, user_id: int) -> Chat | None:
        async with get_session() as session:
            result = await session.execute(_sql.select(Chat).where(_sql.or_(Chat.owner == user_id, Chat.member == user_id)))
            chat = result.scalars().first()
            if not chat.owner:
                return None
            return chat

    @classmethod
    async def find_current_chat(cls, user_id: int) -> Chat | None:
        async with get_session() as session:
            result = await session.execute(
                _sql.select(Chat).where(_sql.or_(Chat.owner == user_id, Chat.member == user_id)))
            chat = result.scalars().first()
            return chat
