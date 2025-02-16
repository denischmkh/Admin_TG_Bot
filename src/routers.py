import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from sql.crud import DBManager

router = Router()

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s [%(asctime)s]: %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d/%m/%Y %I:%M:%S',
                    encoding='utf-8', filemode='w')


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    logging.info(f'User: {message.from_user.username} connected to support bot')
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Связаться с Тех.Поддержкой', callback_data='create_ticket')]
    ])
    await message.answer_photo(photo='https://sun9-15.userapi.com/c837428/v837428321/36c90/RiN2Wf2EntU.jpg',
                               caption='Бу, не испугался? Бойся! Я не друг!, Я тебя обижу, Не иди сюда, Не иди ко мне, не садись рядом со мной',
                               reply_markup=markup)


@router.callback_query(F.data == 'create_ticket')
async def create_ticket(callback: CallbackQuery):
    logging.info(f'User - id:{callback.from_user.id}, username: {callback.from_user.username} Create new ticket')
    result = await DBManager.create_ticket(callback.from_user.id)
    if result == 'Ticket already exists!':
        await callback.answer(result)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Закрыть тикет', callback_data='close_ticket')]
        ])
        await callback.message.edit_caption(caption=f'Ваш тикет #{result} был успешно создан👍\n'
                                                    f'Ожидайте подключения админа🧑‍💻',
                                            reply_markup=markup)

@router.callback_query(F.data == 'close_ticket')
async def close_ticket(callback: CallbackQuery):
    logging.info(f'User - id:{callback.from_user.id}, Username: {callback.from_user.username} Close his ticket')
    result = await DBManager.close_ticket(callback.from_user.id)
    if result == 'Ticket not found!':
        await callback.answer(result)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Связаться с Тех.Поддержкой', callback_data='create_ticket')]
        ])
        await callback.message.edit_caption(photo='https://sun9-15.userapi.com/c837428/v837428321/36c90/RiN2Wf2EntU.jpg',
                                   caption='Бу, не испугался? Бойся! Я не друг!, Я тебя обижу, Не иди сюда, Не иди ко мне, не садись рядом со мной',
                                   reply_markup=markup)