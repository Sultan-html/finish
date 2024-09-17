import aiomysql
import asyncio
from aiogram import types, Router
from app.keyboard import *
from aiogram.filters import Command, CommandStart
router = Router()

user_interactions = {}
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'db': 'bank_db'
}

async def get_db_pool():
    return await aiomysql.create_pool(**db_config)

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("""Привет! Я бот для банковских переводов. Команды, которые я поддерживаю:\n
        /balance - узнать текущий баланс\n
        /transfer - перевести средства\n
        /register - зарегистрировать имя""", reply_markup=keybord)

@router.message(Command('register'))
async def register(message: types.Message):
    user_id = message.from_user.id
    user_interactions[user_id] = {'state': 'waiting_for_name'}
    await message.answer('Введите ваше имя для регистрации:')

@router.message()
async def handle_registration(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_interactions and user_interactions[user_id].get('state') == 'waiting_for_name':
        user_name = message.text
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT INTO users (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=%s', (user_id, user_name, user_name))
                await conn.commit()

        await message.answer("Вы успешно зарегистрированы!")
        user_interactions.pop(user_id, None)
    elif user_id in user_interactions and user_interactions[user_id].get('state') == 'waiting_for_amount':
        await handle_transfer_amount(message)
    elif user_id in user_interactions and user_interactions[user_id].get('state') == 'waiting_for_recipient':
        await handle_transfer_recipient(message)
    else:
        await message.answer("Команда не распознана.")

@router.message(Command('balance'))
async def balance(message: types.Message):
    user_id = message.from_user.id
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT balance FROM users WHERE id = %s', (user_id,))
            result = await cursor.fetchone()

    if result:
        balance = result[0]
        await message.answer(f'Ваш текущий баланс: {balance} сомов')
    else:
        await message.answer('У вас нет зарегистрированного счета. Пожалуйста, зарегистрируйтесь с помощью команды /register')

@router.message(Command('transfer'))
async def transfer_start(message: types.Message):
    user_id = message.from_user.id
    user_interactions[user_id] = {'state': 'waiting_for_amount'}
    await message.answer('Введите сумму для перевода:')

async def handle_transfer_amount(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_interactions and user_interactions[user_id].get('state') == 'waiting_for_amount':
        try:
            amount = float(message.text)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
            
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT balance FROM users WHERE id = %s', (user_id,))
                    result = await cursor.fetchone()

            if not result or result[0] < amount:
                await message.answer('Недостаточно средств на счете.')
                user_interactions.pop(user_id, None)
                return

            user_interactions[user_id]['amount'] = amount
            user_interactions[user_id]['state'] = 'waiting_for_recipient'
            await message.answer('Введите ID получателя:')
        except ValueError:
            await message.answer('Ошибка: введите корректную сумму.')

async def handle_transfer_recipient(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_interactions and user_interactions[user_id].get('state') == 'waiting_for_recipient':
        recipient_id = message.text
        amount = user_interactions[user_id].get('amount')

        if not amount:
            await message.answer('Ошибка: сумма не установлена.')
            user_interactions.pop(user_id, None)
            return

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id FROM users WHERE id = %s', (recipient_id,))
                recipient_exists = await cursor.fetchone() is not None

                if not recipient_exists:
                    await message.answer('Получатель не найден. Пожалуйста, проверьте ID.')
                    user_interactions.pop(user_id, None)
                    return

                await cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (amount, user_id))
                await cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount, recipient_id))
                await conn.commit()

        await message.answer(f'Перевод {amount} сомов успешно выполнен на счет {recipient_id}.')
        user_interactions.pop(user_id, None)
    else:
        await message.answer("Вы не находитесь в процессе перевода.")
