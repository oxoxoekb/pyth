#!/usr/bin/env python3

# Бот для telegram на базе python-telegram-bot
# In TG: @replyboteg_bot
# Создан для изучения python

# Из модуля telegram.ext будем использовать классы:
# Updater - позволяет получать данные и передавать их в dispatcher
# CommandHandler - позволяет описывать команды
# MessageHandler - класс для обработки сообщений
# Filters - класс для различного рода фильтров
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Функция для вызова бота на работу командой "/start"

def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Превед, {first_name}. Какой кубик бросим?")

# Рандом
def rndm1(update, context):
    dice=[0,1]
    update.message.reply_text(f"Выпало значение: {random.choice(dice)}")
def rndm6(update, context):
    dice=[1,2,3,4,5,6]
    update.message.reply_text(f"Выпало значение: {random.choice(dice)}")
def rndm20(update, context):
    dice=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    update.message.reply_text(f"Выпало значение: {random.choice(dice)}")

# Функция вызова помощи командой "/help"
def help(update, context):
    update.message.reply_text('/start - чтобы стартануть, /1d1,/1d6,/1d20 - выбор кубика')

# Функция передачи ошибок в dispatcher
def error(update, context):
    update.message.reply_text('Ошибка, ошибка -_-')

# Функция обработки обычного текста
def text(update, context):
    text_received = update.message.text
    update.message.reply_text(f'Моя твоя не понимайт. Ты написал "{text_received}", а нужно выбрать команду из /help')

def main():
    # Создаем updater и dispatcher для диалога
    # Прячем токен =)
    TOKEN = None
    with open("token.txt") as f:
        TOKEN = f.read().strip()
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # Добавляем обработчики в dispatcher для старта и помощи.
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("1d1", rndm1))
    dispatcher.add_handler(CommandHandler("1d6", rndm6))
    dispatcher.add_handler(CommandHandler("1d20", rndm20))
    # Обработчик для обычного текста
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # Обработчик для ошибок (зачем он мне?)
    dispatcher.add_error_handler(error)
    # запускаем бота используем polling (где-то можно поправить параметры запросов)
    updater.start_polling()
    # Бот работает пока не выключим через Ctrl-C
    updater.idle()
if __name__ == '__main__':
    main()