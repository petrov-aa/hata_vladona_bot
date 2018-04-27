import re
from datetime import datetime

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from hata_vladona.bot.configuration import api_token, vlad_username
from hata_vladona import export
from hata_vladona.configuration import Session
from hata_vladona.models import Camera, CHAT_STATE_WAIT_TIME, CHAT_STATE_WAIT_CAMERA, Chat

bot = TeleBot(api_token)

time_pattern = re.compile('^([0-9]){2}:00$')


@bot.message_handler(commands=['start'])
def send_help(message):
    session = Session()
    chat = Chat()
    chat.id = message.chat.id
    session.add(chat)
    session.commit()
    bot.send_message(message.chat.id, """
Наблюдаем за стройкой квартиры %s в режиме онлайн

/help - Список команд

/last - Последнее фото

Contact - @AlexanderPetrov
Github - https://git.io/vpnaq
""" % vlad_username, disable_web_page_preview=True)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """
/start - Начало работы
/help - Список команд
/last - Последнее фото
/today - Фото за сегодня
/yesterday - Gif за вчера
""")


@bot.message_handler(commands=['cancel'])
def send_last_image(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        chat.state = None
        session.commit()
        bot.send_message(message.chat.id,
                         'Отмена',
                         reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['last'])
def send_last_image(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, 'Нажмите /start и повторите команду')
        return
    camera = session.query(Camera).get(3)
    image = export.get_latest_image(camera)
    photo = open(image.get_file_path(), 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['yesterday'])
def send_past_day_gif(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, 'Нажмите /start и повторите команду')
        return
    camera = session.query(Camera).get(3)
    gif = export.get_past_day_gif(camera)
    document = open(gif.get_file_path(), 'rb')
    result = bot.send_document(message.chat.id, document)
    gif.set_file_id(result.document.file_id)


@bot.message_handler(commands=['today'])
def send_today_image_selector(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, 'Нажмите /start и повторите команду')
        return
    camera = session.query(Camera).get(3)
    images = export.get_today_images(camera)
    if len(images) == 0:
        bot.send_message(message.chat.id,
                         'Изображений за сегодня еще нет')
        return
    markup = ReplyKeyboardMarkup(row_width=2, selective=True)
    for image in images:
        markup.add(KeyboardButton('%02d:00' % image.date.hour))
    chat.state = CHAT_STATE_WAIT_TIME
    session.commit()
    bot.send_message(message.chat.id,
                     'Выберите время или нажмите /cancel для отмены',
                     reply_markup=markup)


@bot.message_handler()
def process_message(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, 'Нажмите /start и повторите команду')
        return
    camera = session.query(Camera).get(3)
    if chat.state == CHAT_STATE_WAIT_TIME:
        text = message.text
        match = time_pattern.match(text)
        if len(match.groups()) != 1:
            bot.send_message(message.chat.id,
                             'Ошибка: Неверный формат времени.' +
                             'Попробуйте другое время или нажмите /cancel для отмены')
            return
        now = datetime.now()
        date = datetime(now.year, now.month, now.day, match.groups()[0])
        image = export.get_image_by_date(camera, date)
        if image is None:
            bot.send_message(message.chat.id,
                             'Ошибка: Изображение за это вермя отсутствует на сервере. ' +
                             'Попробуйте другое время или нажмите /cancel для отмены')
            return
        photo = open(image.get_file_path(), 'rb')
        bot.send_photo(message.chat.id, photo)
        chat.state = None
        session.commit()

