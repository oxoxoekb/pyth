#!/usr/bin/env python3

# Бот для telegram на базе python-telegram-bot
# In TG: @replyboteg_bot
# Создан для изучения python

# Из модуля telegram.ext будем использовать классы:
# Updater - позволяет получать данные и передавать их в dispatcher
# CommandHandler - позволяет описывать команды
# MessageHandler - класс для обработки сообщений
# Filters - класс для различного рода фильтров

# Сделать функцию чека погоды, сделать словарь в который будет вноситься информация по айди юзера и его выбору
# города. Далее уже из этого словаря дергать имя города в кирилице и запускать чек погоды для него.
# Сейчас есть ошибка в том, что не обновляется колбак дата, т.к. кнопки не нажаты. При нажатии на Other
# нужно изменять клавиатуру и сделать 2 кнопки Ок и отмена/назад. После ввода города - жать ОК и переходить
# в другое состояние системы.
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
    ConversationHandler
)
# Ведение журнала логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Этапы/состояния разговора
DORW, DICE, WEATHER, END_OF_THE_END = range(4)
# Данные обратного вызова
WTHR, DCS, EKB, MSK, SPB, OTHER, DICE6, DICE8, DICE20, DICE100 = range(10)
# Словари для кубиков, погоды и пользователей.
DICES = {
    "1d6" : {
        'value' : "6",
        'callback_data': "DICE6"
    },
    "1d8" : {
        'value' : "8",
        'callback_data' : "DICE8"
    },
    "1d20" : {
        'value' : "20",
        'callback_data' : "DICE20"
    },
    "1d100" : {
        'value' : "100",
        'callback_data' : "DICE100"
    }
}
CITIES = {
    "EKB": {
        's_city' : "Екатеринбург",
        'city_id' : "1486209",
        'callback_data' : "EKB"
    },
    "MSK": {
        's_city' : "Москва",
        'city_id' : "524901",
        'callback_data' : "MSK"
    },
    "SPB": {
        's_city' : "Санкт-Петербург",
        'city_id' : "536203",
        'callback_data' : "SPB"
    },
    "OTHER": {
        's_city' : "Другой город",
        'city_id' : "Неизвестен",
        'callback_data' : "OTHER"
    }
}
USERS = {
    "User": {
        "User ID" : "user.id",
        "Name" : "user.first_name"
    }
}

def start(update, _):
    """Вызывается по команде `/start`."""
    # Получаем пользователя, который запустил команду `/start`
    user = update.message.from_user
    logger.info("Пользователь %s начал разговор", user.first_name)
    # Создаем `InlineKeyboard`, где каждая кнопка имеет
    # отображаемый текст и строку `callback_data`
    # Клавиатура - это список строк кнопок, где каждая строка,
    # в свою очередь, является списком `[[...]]`
    keyboard = [
        [
            InlineKeyboardButton("Кубики", callback_data='DCS'),
            InlineKeyboardButton("Погода", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Отправляем сообщение с текстом и добавленной клавиатурой `reply_markup`
    update.message.reply_text(
        text="Кубики или погода?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас состояние `DORW`
    return DORW

def start_over(update, _):
    """Тот же текст и клавиатура, что и при `/start`, но не как новое сообщение"""
    # Получаем `CallbackQuery` из обновления `update`
    query = update.callback_query
    # На запросы обратного вызова необходимо ответить,
    # даже если уведомление для пользователя не требуется.
    # В противном случае у некоторых клиентов могут возникнуть проблемы.
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Кубики", callback_data='DCS'),
            InlineKeyboardButton("Погода", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
   # Отредактируем сообщение, вызвавшее обратный вызов.
   # Это создает ощущение интерактивного меню.
    query.edit_message_text(
        text="Кубики или погода?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `DORW`
    return DORW


def text(update, context):
    first_name = update.message.chat.first_name
    text_received = update.message.text
    update.message.reply_text(f'Превед, {first_name}! Ты написал "{text_received}", а надо нажать на /start ;)')


def check_dice(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1d6", callback_data=DICES['1d6']['callback_data']),
            InlineKeyboardButton("1d8", callback_data=DICES['1d8']['callback_data']),
            InlineKeyboardButton("1d20", callback_data=DICES['1d20']['callback_data']),
            InlineKeyboardButton("1d100", callback_data=DICES['1d100']['callback_data']),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Какой кубик кинем?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `DICE`
    return DICE

def random_dice(update, _):
    # Функция в зависимости от callback_data возвращает случайное значение кубика
    query = update.callback_query
    dice_data = query['data']
    query.answer()
    if dice_data == 'DICE6':
        dicer = range(1, 7)
    elif dice_data == 'DICE8':
        dicer = range(1, 9)
    elif dice_data == 'DICE20':
        dicer = range(1, 21)
    else:
        dicer = range(1, 101)
    keyboard = [
        [
            InlineKeyboardButton("Да, сделаем это снова!", callback_data='DCS'),
            InlineKeyboardButton("Нет, с меня хватит ...", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Выпало значение: {random.choice(dicer)}", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `END_OF_THE_END`
    return END_OF_THE_END


def choose_city(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Екатеринбург", callback_data=CITIES['EKB']['callback_data']),
            InlineKeyboardButton("Москва", callback_data=CITIES['MSK']['callback_data']),
            InlineKeyboardButton("Санкт-Петербург", callback_data=CITIES['SPB']['callback_data']),
            InlineKeyboardButton("Другой (указать вручную)", callback_data=CITIES['OTHER']['callback_data']),
            InlineKeyboardButton("Назад", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="В каком городе узнаем погоду?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `WEATHER`
    return WEATHER


# тут сделать вывод кнопок ок и назад.
def weather_other(update, _):
    user = update.message.from_user
    logger.info("Проверка погоды в городе", update.message.text, "для", user.first_name)
    # Токен спрятан в файле
    OWtoken = None
    with open("ow.txt") as f:
        OWtoken = f.read().strip()
    s_city = update.message.text
    city_id = 0
    # Ищем город
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': OWtoken})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        print("city:", cities)
        city_id = data['list'][0]['id']
        print('city_id=', city_id)
        # сначала сделать запрос res/find и уже после него try - if если найден город - выполнять, иначе - выводить
        # ошибку.
    except Exception as e:
        print("Указанный город не найден, ошибка:", e)
        pass
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': OWtoken})
    data = res.json()
    # Для дебага вывожу в консоль результат поиска.
    print(f"В г. {s_city} сейчас {data['weather'][0]['description']},"
          f" температура {data['main']['temp']} °C. Попробуем еще раз?")
    # query = update.callback_query
    # query.answer()
    return city_id

def search_city(s_city):
    # Если я определяю заранее
    # Нужно найти ключ по значению и вывести город-параметр-ы_сити
    OWtoken = None
    with open("ow.txt") as f:
        OWtoken = f.read().strip()
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': OWtoken})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        print("city:", cities)
        city_id = data['list'][0]['id']
        print('city_id =', city_id)
        # сначала сделать запрос res/find и уже после него try - if если найден город - выполнять, иначе - выводить
        # ошибку.
    except Exception as e:
        print("Указанный город не найден, ошибка:", e)
        pass
    return city_id


def enter_city (update, _):
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("Ок", callback_data='EKB'),
            InlineKeyboardButton("Рестарт", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f'Введите город и для проодолжения нажмите "ОК"'
             f' Попробовать еще раз - кнопка "Рестарт"',
        reply_markup=reply_markup
    )
    return WEATHER


def weather_api(update, _):
    """Показ выбора кнопок"""
    # Запрашиваем погоду через ID на openweatherman.org
    # Токен спрятан в файле
    # print(update.message.text)
    query = update.callback_query
    print(query['data'])
    s_data = query['data']
    for v in CITIES.keys():
        if v == s_data:
            s_city = CITIES[v]['s_city']
            print(s_city, "dddd")
        else: s_city = update.message.text
    city_id = search_city(s_city)
    print(city_id, "получили ID города")
    OWtoken = None
    with open("ow.txt") as f:
        OWtoken = f.read().strip()
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': OWtoken})
    data = res.json()
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Да, сделаем это снова!", callback_data='DCS'),
            InlineKeyboardButton("Нет, спасибо.", callback_data='WTHR'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"В г. {s_city} сейчас {data['weather'][0]['description']},"
             f" температура {data['main']['temp']} °C. Попробуем еще раз?",
        reply_markup=reply_markup
    )
    return END_OF_THE_END

def end(update, _):
    """Возвращает `ConversationHandler.END`, который говорит
    `ConversationHandler` что разговор окончен"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Всего доброго!")
    return ConversationHandler.END


if __name__ == '__main__':
    TOKEN = None
    with open("token.txt") as f:
        TOKEN = f.read().strip()
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Настройка обработчика разговоров с состояниями
    # Используем параметр `pattern` для передачи `CallbackQueries` с
    # определенным шаблоном данных соответствующим обработчикам
    # ^ - означает "начало строки"
    # $ - означает "конец строки"
    # Таким образом, паттерн `^ABC$` будет ловить только 'ABC'
    conv_handler = ConversationHandler(
        # точка входа в разговор
        entry_points=[CommandHandler('start', start)],
        # словарь состояний разговора, возвращаемых callback функциями
        states={
            # Ответ пользователя на это сообщение будет
            # обрабатываться обработчиками определенными в этом списке
            DORW: [
                CallbackQueryHandler(check_dice, pattern='^DCS$'),
                CallbackQueryHandler(choose_city, pattern='^WTHR$'),
            ],
            DICE: [
                CallbackQueryHandler(random_dice, pattern='^DICE6$'),
                CallbackQueryHandler(random_dice, pattern='^DICE8$'),
                CallbackQueryHandler(random_dice, pattern='^DICE20$'),
                CallbackQueryHandler(random_dice, pattern='^DICE100$'),
            ],
            WEATHER: [
                CallbackQueryHandler(weather_api, pattern='^EKB$'),
                CallbackQueryHandler(weather_api, pattern='^MSK$'),
                CallbackQueryHandler(weather_api, pattern='^SPB$'),
                CallbackQueryHandler(enter_city, pattern='^OTHER$'),
                CallbackQueryHandler(start_over, pattern='^WTHR$'),
                MessageHandler(Filters.text, enter_city),
            ],
            END_OF_THE_END: [
                CallbackQueryHandler(start_over, pattern='^DCS$'),
                CallbackQueryHandler(end, pattern='^WTHR$'),
            ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('start', start)],
    )

    # Добавляем `ConversationHandler` в диспетчер, который
    # будет использоваться для обработки обновлений
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    updater.start_polling()
    updater.idle()