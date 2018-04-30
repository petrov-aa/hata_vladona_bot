import os
import re
from datetime import datetime, timedelta
from telebot import TeleBot, apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from hata_vladona.config import bot_config, proxy_config
from hata_vladona import export
from hata_vladona.database import database
from hata_vladona.messages import *
from hata_vladona.models import Camera, CHAT_STATE_WAIT_TIME, CHAT_STATE_WAIT_CAMERA, Chat, Image


if bot_config['use_proxy']:
    apihelper.proxy = {'https': '%s://%s:%s@%s:%s' % (proxy_config['protocol'],
                                                      proxy_config['user'],
                                                      proxy_config['password'],
                                                      proxy_config['host'],
                                                      proxy_config['port'])}

bot = TeleBot(bot_config['token'])

time_pattern = re.compile('^([0-9]{2}):00$')


@bot.message_handler(commands=['start'])
def send_help(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        chat = Chat()
        chat.id = message.chat.id
        chat.camera_id = 3
        session.add(chat)
        session.commit()
    bot.send_message(message.chat.id,
                     BOT_START % bot_config['vlad_username'],
                     disable_web_page_preview=True)


@bot.message_handler(commands=['help'])
def send_help(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    bot.send_message(message.chat.id, BOT_HELP % chat.camera.name, parse_mode='Markdown')


@bot.message_handler(commands=['cancel'])
def send_last_image(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    if chat.state is not None:
        chat.state = None
        session.commit()
    bot.send_message(message.chat.id,
                     BOT_CANCEL,
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['last'])
def send_last_image(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    image = export.get_latest_image(camera)
    photo = open(image.get_file_path(), 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['yesterday'])
def send_past_day_gif(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    gif = export.get_past_day_gif(camera)
    document = open(gif.get_file_path(), 'rb')
    result = bot.send_document(message.chat.id, document)
    gif.file_id = result.document.file_id
    session.commit()


@bot.message_handler(commands=['today'])
def send_today_image_selector(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    images = export.get_today_images(camera)
    if len(images) == 0:
        bot.send_message(message.chat.id, BOT_NO_TODAY_IMAGES)
        return
    markup = ReplyKeyboardMarkup(row_width=2, selective=True)
    for image in images:
        markup.add(KeyboardButton('%02d:00' % image.date.hour))
    chat.state = CHAT_STATE_WAIT_TIME
    session.commit()
    bot.send_message(message.chat.id,
                     BOT_CHOOSE_TIME,
                     reply_markup=markup)


@bot.message_handler(commands=['setcamera'])
def set_camera_message(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    chat.state = CHAT_STATE_WAIT_CAMERA
    session.commit()
    markup = ReplyKeyboardMarkup()
    cameras = session.query(Camera).all()
    for camera in cameras:
        markup.add(KeyboardButton(camera.name))
    bot.send_message(message.chat.id, BOT_CHOOSE_CAMERA, reply_markup=markup)


@bot.message_handler()
def process_message(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    if chat.state == CHAT_STATE_WAIT_TIME:
        text = message.text
        match = time_pattern.match(text)
        if len(match.groups()) != 1:
            bot.send_message(message.chat.id,
                             BOT_CHOOSE_TIME_FORMAT_ERROR)
            return
        now = datetime.now()
        date = datetime(now.year, now.month, now.day, int(match.groups()[0]))
        if now.hour < Image.hour_start:
            date = date - timedelta(days=1)
        image = export.get_image_by_date(camera, date)
        if image is None or not os.path.exists(image.get_file_path()):
            bot.send_message(message.chat.id,
                             BOT_CHOOSE_TIME_NO_IMAGE_ERROR)
            return
        photo = open(image.get_file_path(), 'rb')
        bot.send_photo(message.chat.id, photo, reply_markup=ReplyKeyboardRemove())
        chat.state = None
        session.commit()
    if chat.state == CHAT_STATE_WAIT_CAMERA:
        text = message.text
        new_camera = session.query(Camera).filter(Camera.name == text).first()
        if new_camera is None:
            bot.send_message(message.chat.id,
                             BOT_CHOOSE_CAMERA_ERROR)
            return
        chat.camera = new_camera
        chat.state = None
        session.commit()
        bot.send_message(message.chat.id,
                         BOT_CHOOSE_CAMERA_SUCCESS % new_camera.name,
                         parse_mode='Markdown',
                         reply_markup=ReplyKeyboardRemove())

