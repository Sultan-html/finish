import asyncio
import logging
from aiogram import types,Bot,Dispatcher,F,Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.filters import Command
from database import get_db_connection, init_db
from app.keyboard import *

router = Router()

class TransferState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_recipient = State()
    waiting_for_name = State()


async def start(message: types.Message):
    await message.answer("""Привет! Я бот для банковских переводов. Команды, которые я поддерживаю:\n
        /balance - узнать текущий баланс\n
        /transfer - перевести средства\n
        /register - зарегистрировать имя""", reply_markup=keybord)


async def register(message: types.Message):
    await message.answer('Введите ваше имя для регистрации:')
    await TransferState.waiting_for_name.set()

async def register_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (id, name) VALUES (?, ?)', (user_id, user_name))
        conn.commit()

    await message.answer("Вы успешно зарегистрированы!")
    await state.finish()

async def balance(message: types.Message):
    user_id = message.from_user.id

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

    if result:
        balance = result[0]
        await message.answer(f'Ваш текущий баланс: {balance} сомов')
    else:
        await message.answer('У вас нет зарегистрированного счета. Пожалуйста, зарегистрируйтесь с помощью команды /register')


async def transfer_start(message: types.Message):
    await message.answer('Введите сумму для перевода:')
    await TransferState.waiting_for_amount.set()

async def transfer_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной.")
        
        user_id = message.from_user.id

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()

        if not result or result[0] < amount:
            await message.answer('Недостаточно средств на счете.')
            await state.finish()
            return

        await state.update_data(amount=amount)
        await message.answer('Введите ID получателя:')
        await TransferState.waiting_for_recipient.set()
    except ValueError:
        await message.answer('Ошибка: введите корректную сумму.')

async def transfer_recipient(message: types.Message, state: FSMContext):
    recipient_id = message.text
    user_data = await state.get_data()
    amount = user_data.get('amount')

    if not amount:
        await message.answer('Ошибка: сумма не установлена.')
        await state.finish()
        return

    user_id = message.from_user.id

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE id = ?', (recipient_id,))
        recipient_exists = cursor.fetchone() is not None

        if not recipient_exists:
            await message.answer('Получатель не найден. Пожалуйста, проверьте ID.')
            await state.finish()
            return

        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
        conn.commit()

    await message.answer(f'Перевод {amount} сомов успешно выполнен на счет {recipient_id}.')
    await state.finish()
