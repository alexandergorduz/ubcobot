from telebot.types import ReplyKeyboardMarkup, KeyboardButton

start_creating_button = KeyboardButton(text='Начать создание КП')
keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard1.add(start_creating_button)

continue_button = KeyboardButton(text='Добавлены все позиции')
abort_button = KeyboardButton(text='Отмена')
keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard2.add(continue_button)
keyboard2.add(abort_button)

keyboard3 = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard3.add(abort_button)