import os
import re
import logging
import dateparser
from datetime import datetime, timedelta

from telebot import TeleBot, apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot import logger

from hata_vladona.config import bot_config, proxy_config
from hata_vladona import export
from hata_vladona.database import commit_session
from hata_vladona.messages import *
from hata_vladona.models import Camera,\
    CHAT_STATE_WAIT_TIME, CHAT_STATE_WAIT_CAMERA, Chat, Image, Message

if bot_config['use_proxy']:
    apihelper.proxy = {'https': '%s://%s:%s@%s:%s' % (proxy_config['protocol'],
                                                      proxy_config['user'],
                                                      proxy_config['password'],
                                                      proxy_config['host'],
                                                      proxy_config['port'])}

# logger.setLevel(logging.DEBUG)


bot = TeleBot(bot_config['token'])

time_pattern = re.compile('^([0-9]{2}):00$')


@bot.message_handler(commands=['start'])
@commit_session
def send_help(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        chat = Chat()
        chat.telegram_chat_id = message.chat.id
        chat.camera_id = 3
        session.add(chat)
        session.flush()
    bot.send_message(message.chat.id,
                     BOT_START % (bot_config['vlad_username']),
                     disable_web_page_preview=True)


@bot.message_handler(commands=['help'])
@commit_session
def send_help(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    bot.send_message(message.chat.id,
                     BOT_HELP % chat.camera.name,
                     parse_mode='Markdown')


@bot.message_handler(commands=['cancel'])
@commit_session
def send_last_image(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    if chat.state is not None:
        chat.state = None
        session.flush()
    bot.send_message(message.chat.id,
                     BOT_CANCEL,
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['last'])
@commit_session
def send_last_image(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    image = export.get_latest_image(camera)
    photo = open(image.get_file_path(), 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['yesterday', 'week', 'month', 'full'])
@commit_session
def send_past_week_gif(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    camera = chat.camera
    if message.text.startswith('/yesterday'):
        gif = export.get_past_day_gif(camera)
    elif message.text.startswith('/week'):
        gif = export.get_past_week_gif(camera)
    elif message.text.startswith('/month'):
        gif = export.get_past_month_gif(camera)
    elif message.text.startswith('/full'):
        gif = export.get_full_gif(camera)
    else:
        return
    gif_file_path = gif.get_file_path()
    if not os.path.exists(gif_file_path):
        bot.send_message(message.chat.id, BOT_ERROR_NO_GIF_FILE)
        return
    if gif.file_id:
        bot.send_document(message.chat.id, gif.file_id)
    else:
        msg = Message()
        result = bot.send_message(message.chat.id, BOT_VIDEO_UPLOAD)
        msg.telegram_message_id = result.message_id
        msg.gif = gif
        msg.chat = chat
        session.add(msg)
        session.flush()
        document = open(gif.get_file_path(), 'rb')
        result = bot.send_document(message.chat.id, document)
        gif.file_id = result.document.file_id
        bot.delete_message(msg.chat.telegram_chat_id, msg.telegram_message_id)
        session.delete(msg)
        session.flush()


@bot.message_handler(commands=['today'])
@commit_session
def send_today_image_selector(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
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
    session.flush()
    bot.send_message(message.chat.id,
                     BOT_CHOOSE_TIME,
                     reply_markup=markup,
                     reply_to_message_id=message.message_id)


@bot.message_handler(commands=['setcamera'])
@commit_session
def set_camera_message(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    if chat is None:
        bot.send_message(message.chat.id, BOT_RESTART)
        return
    chat.state = CHAT_STATE_WAIT_CAMERA
    session.flush()
    markup = ReplyKeyboardMarkup(selective=True)
    cameras = session.query(Camera).all()
    for camera in cameras:
        markup.add(KeyboardButton(camera.name))
    bot.send_message(message.chat.id,
                     BOT_CHOOSE_CAMERA,
                     reply_markup=markup,
                     reply_to_message_id=message.message_id)


@bot.message_handler(commands=['donate'])
def send_donation_link(message):
    bot.send_message(message.chat.id, bot_config['donation_url'])


@bot.message_handler(content_types=['text'])
@commit_session
def process_message(message, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
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
        session.flush()
    elif chat.state == CHAT_STATE_WAIT_CAMERA:
        text = message.text
        new_camera = session.query(Camera).filter(Camera.name == text).first()
        if new_camera is None:
            bot.send_message(message.chat.id,
                             BOT_CHOOSE_CAMERA_ERROR)
            return
        chat.camera = new_camera
        chat.state = None
        session.flush()
        bot.send_message(message.chat.id,
                         BOT_CHOOSE_CAMERA_SUCCESS % new_camera.name,
                         parse_mode='Markdown',
                         reply_markup=ReplyKeyboardRemove())
    else:
        if chat.state is not None:
            return
        text = message.text.strip()
        parsed_date = dateparser.parse(text, languages=['ru', 'en'])
        if parsed_date is None:
            return
        now = datetime.now()
        if parsed_date > now:
            bot.send_message(message.chat.id, ':(')
            return
        date = datetime(parsed_date.year, parsed_date.month, parsed_date.day, parsed_date.hour)
        if Image.hour_start <= parsed_date.hour <= Image.hour_end:
            image = Image.get_by_date(camera, date)
        else:
            image = Image.get_day_first_image(camera,
                                              datetime(parsed_date.year, parsed_date.month, parsed_date.day))
        if image is not None:
            photo = open(image.get_file_path(), 'rb')
            bot.send_photo(message.chat.id, photo)
        else:
            first_image = Image.get_first_image(camera)
            if first_image is None:
                return
            if date < first_image.date:
                bot.send_message(message.chat.id, BOT_IMAGE_AVAILABLE_FROM % (first_image.date.day,
                                                                              first_image.date.month,
                                                                              first_image.date.year))
            else:
                bot.send_message(message.chat.id, BOT_IMAGE_NOT_AVAILABLE)
