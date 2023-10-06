#!/usr/bin/env python3

# Бот для telegram на базе python-telegram-bot
# In TG: @replyboteg_bot
# Создан для изучения python

# Из модуля telegram.ext будем использовать классы:
# Updater - позволяет получать данные и передавать их в dispatcher
# CommandHandler - позволяет описывать команды
# MessageHandler - класс для обработки сообщений
# Filters - класс для различного рода фильтров
#
import random, requests, logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
)
# Ведение журнала логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

Функция для вызова бота на работу командой "/start"
def start(update, context):
   first_name = update.message.chat.first_name
   update.message.reply_text(f"Превед, {first_name}. Кидаем кубик или узнаем погоду?")

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

# Функция проверки погоды
def check_weather(update, context):
   # Запрашиваем погоду в Екб через ID на openweatherman.org
   OWtoken = None
   city_id = 1486209
   with open("ow.txt") as f:
       OWtoken = f.read().strip()
   res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': OWtoken})
   data = res.json()
   #update.message.reply_text(f"В Екатеринбурге сейчас {data}")
   update.message.reply_text(f"В Екатеринбурге сейчас {data['weather'][0]['description']},"
                             f" температура {data['main']['temp']} °C")

# Функция описания кнопок inline
def start2(update: Update, context: CallbackContext):
   keyboard = [
       [
           InlineKeyboardButton("Москва", callback_data='dasd'),
           InlineKeyboardButton("Питер", callback_data='123123123123123123'),
       ],
       [
           InlineKeyboardButton("Екб", callback_data='1231231231'),
           InlineKeyboardButton("Другой", callback_data='123123')
       ],
   ]
   reply_markup = InlineKeyboardMarkup(keyboard)
   update.message.reply_text('В каком городе будем смотреть прогноз погоды?', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
   """Parses the CallbackQuery and updates the message text."""
   query = update.callback_query
   query.answer()
   query.edit_message_text(text=f"Selected option: {query.data}")
   #if callbackcontext = // проверяем, что за запрос был и отвечаем на него.

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
   dispatcher.add_handler(CommandHandler("start2", start2))
   dispatcher.add_handler(CommandHandler("help", help))
   # Добавляем обработчики в dispatcher для кубиков.
   dispatcher.add_handler(CommandHandler("1d1", rndm1))
   dispatcher.add_handler(CommandHandler("1d6", rndm6))
   dispatcher.add_handler(CommandHandler("1d20", rndm20))
   # Добавляем обработчики в dispatcher для вызова погоды.
   dispatcher.add_handler(CommandHandler("weather", check_weather))
   dispatcher.add_handler(CallbackQueryHandler(button))
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
