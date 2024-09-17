from aiogram import Bot, Dispatcher,F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup



buttons = [
    [KeyboardButton(text='/balance'),KeyboardButton(text='/transfer'),KeyboardButton(text='/register')]
]
keybord = ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)