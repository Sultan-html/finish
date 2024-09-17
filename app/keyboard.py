from aiogram import Bot, Dispatcher,F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandStart


buttons = [
    [KeyboardButton(text='/balance'),KeyboardButton(text='/transfer'),KeyboardButton(text='/register')]
]
keybord = ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)