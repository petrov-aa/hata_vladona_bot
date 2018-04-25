from telebot import TeleBot, types

from hata_vladona.bot.configuration import api_token
from hata_vladona import export
from hata_vladona.configuration import Session

bot = TeleBot(api_token)


@bot.message_handler(commands=['start'])
def send_help(message):
    bot.send_message(message.chat.id, """
Наблюдаем за стройкой квартиры Влада в режиме онлайн

/help - Список команд

/last - Последнее фото

Contact - @AlexanderPetrov
Github - https://git.io/vpnaq
""", disable_web_page_preview=True)


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
    image = export.get_latest_image()
    photo = open(image.get_file_path(), 'rb')
    result = bot.send_photo(message.chat.id, photo)
    print(result)


@bot.message_handler(commands=['yesterday'])
def send_past_day_gif(message):
    gif = export.get_past_day_gif()
    document = open(gif.get_file_path(), 'rb')
    result = bot.send_document(message.chat.id, document)
    gif.set_file_id(result.document.file_id)
