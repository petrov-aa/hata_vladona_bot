import os

from configparser import ConfigParser

config_file = './config.ini'

if not os.path.exists(config_file):
    raise FileNotFoundError('Файл с конфигурацией не найден')

config = ConfigParser()
config.read(config_file)

if 'Bot' not in config:
    raise AttributeError('Не заданы параметры бота')

if 'token' not in config['Bot']:
    raise AttributeError('Не задан API TOKEN')

api_token = config['Bot']['token']

vlad_username = config['Bot']['vlad_username'] if 'vlad_username' in config['Bot'] else ''


