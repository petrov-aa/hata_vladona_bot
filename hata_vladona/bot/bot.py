from telebot import TeleBot

from hata_vladona.bot.configuration import api_token, vlad_username
from hata_vladona import export
from hata_vladona.configuration import session
from hata_vladona.models import Camera

bot = TeleBot(api_token)


@bot.message_handler(commands=['start'])
def send_help(message):
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
/yesterday - Gif за вчера
""")


@bot.message_handler(commands=['last'])
def send_last_image(message):
    camera = session.query(Camera).get(3)
    image = export.get_latest_image(camera)
    photo = open(image.get_file_path(), 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['yesterday'])
def send_past_day_gif(message):
    camera = session.query(Camera).get(3)
    gif = export.get_past_day_gif(camera)
    document = open(gif.get_file_path(), 'rb')
    result = bot.send_document(message.chat.id, document)
    gif.set_file_id(result.document.file_id)
