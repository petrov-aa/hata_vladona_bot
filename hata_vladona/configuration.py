import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser

config_file = './config.ini'

if not os.path.exists(config_file):
    raise FileNotFoundError('Файл с конфигурацией не найден')

config = ConfigParser()
config.read(config_file)

if 'Database' not in config:
    raise AttributeError('Не заданы параметры базы данных')
if 'dialect' not in config['Database']:
    raise AttributeError('Не задан тип базы данных')
if 'host' not in config['Database']:
    raise AttributeError('Не задан хост базы данных')
if 'user' not in config['Database']:
    raise AttributeError('Не задан пользователь базы данных')
if 'password' not in config['Database']:
    raise AttributeError('Не задан пароль базы данных')
if 'name' not in config['Database']:
    raise AttributeError('Не задано имя базы данных')

__db_dialect = config['Database']['dialect']
__db_driver = config['Database']['driver']
__db_host = config['Database']['host']
__db_user = config['Database']['user']
__db_password = config['Database']['password']
__db_name = config['Database']['name']

__engine_url = URL(__db_dialect + '+' + __db_driver)
__engine_url.username = __db_user if __db_user else None
__engine_url.password = __db_password if __db_password else None
__engine_url.host = __db_host if __db_host else None
__engine_url.database = __db_name if __db_name else None

engine = create_engine(__engine_url)

engine_url = str(__engine_url)

if 'Storage' not in config:
    raise AttributeError('Не заданы параметры хранилища')
if 'path' not in config['Storage']:
    raise AttributeError('Не задано место хранения загружаемых изображений')

storage_path = config['Storage']['path']

if 'Gif' not in config:
    raise AttributeError('Не заданы параметры gif')
if 'path' not in config['Gif']:
    raise AttributeError('Не задано место хранения gif')

gif_path = config['Gif']['path']

__Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()
