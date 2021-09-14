#!/usr/bin/env python3

# Бот для telegram на базе python-telegram-bot
# In TG: @replyboteg_bot

# Из модуля telegram.ext будем использовать классы:
# Updater - позволяет получать данные и передавать их в dispatcher
# CommandHandler - позволяет описывать команды
# MessageHandler - класс для обработки сообщений
# Filters - класс для различного рода фильтров

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Функция для вызова бота на работу командой "/startuem"
def start(update, context):
    update.message.reply_text('Да работаю я, работаю -_-')
# Функция вызова помощи командой "/help"
def help(update, context):
    update.message.reply_text('Нехочунебуду -_-, но вообще можешь написать /startuem')
# Функция передачи ошибок в dispatcher
def error(update, context):
    update.message.reply_text('Ошибка, ошибка -_-')
# Функция обработки обычного текста
def text(update, context):
    text_received = update.message.text
    update.message.reply_text(f'Зачем ты мне написал: "{text_received}" ?')
def main():
    # Создаем updater и dispatcher для диалога
    # Прячем токен =)
    TOKEN = None
    with open("token.txt") as f:
        TOKEN = f.read().strip()
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # Добавляем обработчики в dispatcher для старта и помощи.
    dispatcher.add_handler(CommandHandler("startuem", start))
    dispatcher.add_handler(CommandHandler("help", help))
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