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
            InlineKeyboardButton("Кубики", callback_data=str(DCS)),
            InlineKeyboardButton("Погода", callback_data=str(WTHR)),
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
            InlineKeyboardButton("Кубики", callback_data=str(DCS)),
            InlineKeyboardButton("Погода", callback_data=str(WTHR)),
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
            InlineKeyboardButton("1d6", callback_data=str(DICE6)),
            InlineKeyboardButton("1d8", callback_data=str(DICE8)),
            InlineKeyboardButton("1d20", callback_data=str(DICE20)),
            InlineKeyboardButton("1d100", callback_data=str(DICE100)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Какой кубик кинем?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `DICE`
    return DICE


def check_weather(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Екатеринбург", callback_data=str(EKB)),
            InlineKeyboardButton("Москва", callback_data=str(MSK)),
            InlineKeyboardButton("Санкт-Петербург", callback_data=str(SPB)),
            InlineKeyboardButton("Другой (указать вручную)", callback_data=str(OTHER)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="В каком городе узнаем погоду?", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `WEATHER`
    return WEATHER

def random_dice(update, _):
    # А вот эта функция работает криво, т.к if - не работает...
    query = update.callback_query
    dice_data = {query['data']}
    print(dice_data)
    query.answer()
    print(query.answer)
    # Если я определяю заранее
    dicer = range(1, 100)
    if dice_data == '6':
        dicer = range(1, 7)
        print(dicer)
    elif dice_data == '7':
        dicer = range(1, 9)
    elif dice_data == '8':
        dicer = range(1, 21)
    elif dice_data == '9':
        dicer = range(1, 101)
    keyboard = [
        [
            InlineKeyboardButton("Да, сделаем это снова!", callback_data=str(DCS)),
            InlineKeyboardButton("Нет, с меня хватит ...", callback_data=str(WTHR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Выпало значение: {random.choice(dicer)}", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `END_OF_THE_END`
    return END_OF_THE_END

def weather_api(update, _):
    """Показ выбора кнопок"""
    # Запрашиваем погоду в ЕКБ (далее будем подставлять ID выбранного города) через ID на openweatherman.org
    # Токен спрятан в файле
    OWtoken = None
    city_id = 1486209
    with open("ow.txt") as f:
        OWtoken = f.read().strip()
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': OWtoken})
    data = res.json()
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Да, сделаем это снова!", callback_data=str(DCS)),
            InlineKeyboardButton("Нет, спасибо.", callback_data=str(WTHR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"В Екатеринбурге сейчас {data['weather'][0]['description']},"
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
                CallbackQueryHandler(check_dice, pattern='^' + str(DCS) + '$'),
                CallbackQueryHandler(check_weather, pattern='^' + str(WTHR) + '$'),
            ],
            DICE: [
                CallbackQueryHandler(random_dice, pattern='^' + str(DICE6) + '$'),
                CallbackQueryHandler(random_dice, pattern='^' + str(DICE8) + '$'),
                CallbackQueryHandler(random_dice, pattern='^' + str(DICE20) + '$'),
                CallbackQueryHandler(random_dice, pattern='^' + str(DICE100) + '$'),
            ],
            WEATHER: [
                CallbackQueryHandler(weather_api, pattern='^' + str(EKB) + '$'),
                CallbackQueryHandler(weather_api, pattern='^' + str(MSK) + '$'),
                CallbackQueryHandler(weather_api, pattern='^' + str(SPB) + '$'),
                CallbackQueryHandler(weather_api, pattern='^' + str(OTHER) + '$'),
            ],
            END_OF_THE_END: [
                CallbackQueryHandler(start_over, pattern='^' + str(DCS) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(WTHR) + '$'),
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