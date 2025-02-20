import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from init_bot import bot
from sql.crud import DBManager
from state import States

router = Router()

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s [%(asctime)s]: %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d/%m/%Y %I:%M:%S',
                    encoding='utf-8', filemode='w')

admins = [680650067]


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    logging.info(f'User: {message.from_user.username} connected to support bot')
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Связаться с Тех.Поддержкой', callback_data='create_ticket')]
    ])
    await message.answer_photo(photo='https://sun9-15.userapi.com/c837428/v837428321/36c90/RiN2Wf2EntU.jpg',
                               caption='Бу, не испугался? Бойся! Я не друг!, Я тебя обижу, Не иди сюда, Не иди ко мне, не садись рядом со мной',
                               reply_markup=markup)
    await message.delete()
    await state.set_state(States.in_chat)


@router.message(Command('help'))
async def help_msg(message: Message):
    if message.from_user.id not in admins:
        await message.answer(text='/start - Запустить бота')
    else:
        await message.answer(text='/start - Запустить бота\n'
                                  '/create_chat - Создать чат\n'
                                  '/next_ticket - Следующий тикет\n'
                                  '/close_chat - Закрыть чат')
    await message.delete()


@router.callback_query(F.data == 'create_ticket')
async def create_ticket(callback: CallbackQuery, state: FSMContext):
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


@router.callback_query(F.data == 'close_ticket', States.in_chat)
async def close_ticket(callback: CallbackQuery, state: FSMContext):
    logging.info(f'User - id:{callback.from_user.id}, Username: {callback.from_user.username} Close his ticket')
    result = await DBManager.close_ticket(callback.from_user.id)
    if isinstance(result, str):
        await callback.answer(result)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Связаться с Тех.Поддержкой', callback_data='create_ticket')]
    ])
    await callback.message.edit_caption(
        caption='Бу, не испугался? Бойся! Я не друг!, Я тебя обижу, Не иди сюда, Не иди ко мне, не садись рядом со мной',
        reply_markup=markup
    )
    await state.set_state(States.in_menu)


@router.callback_query(F.data == 'close_ticket', States.in_menu)
async def close_ticket(callback: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Связаться с Тех.Поддержкой', callback_data='create_ticket')]
    ])
    await callback.message.edit_caption(
        caption='Бу, не испугался? Бойся! Я не друг!, Я тебя обижу, Не иди сюда, Не иди ко мне, не садись рядом со мной',
        reply_markup=markup
    )


@router.message(Command('create_chat'))
async def create_chat(message: Message):
    if message.from_user.id not in admins:
        await message.answer('У вас недостаточно прав')
    result = await DBManager.create_chat(message.from_user.id)
    await message.answer(result)
    await message.delete()


@router.message(Command('close_chat'))
async def close_chat(message: Message):
    if message.from_user.id not in admins:
        await message.answer('У вас недостаточно прав')
    result = await DBManager.close_chat(message.from_user.id)
    if result == 'Chat not found!':
        await message.answer(result)
    else:
        await message.answer(result)
        await message.delete()


@router.message(Command('next_ticket'))
async def select_next_ticket(message: Message):
    if message.from_user.id not in admins:
        await message.answer('У вас недостаточно прав')
    result = await DBManager.select_next_ticket(message.from_user.id)
    if isinstance(result, str):
        await message.answer(result)
        return
    await message.answer(text=f'Текущий чат с {result.member}')
    await message.delete()
    await bot.send_message(chat_id=result.member, text='Админ законектился, задавай вопрос...')


@router.message()
async def send_message_to_opponent(message: Message):
    current_chat = await DBManager.get_chat(message.from_user.id)
    if not current_chat:
        return
    if message.from_user.id == current_chat.owner:
        await bot.send_message(chat_id=current_chat.member, text=message.text)
    else:
        await bot.send_message(chat_id=current_chat.owner, text=message.text)


