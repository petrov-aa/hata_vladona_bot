from configparser import ConfigParser

class ConfigError(Exception):
    pass

config_file = './config.ini'

config = ConfigParser()
config.read(config_file)

if 'Database' not in config:
    raise ConfigError('Не заданы параметры базы данных')
if 'driver' not in config['Database']:
    raise ConfigError('Не задан тип базы данных')
if 'host' not in config['Database']:
    raise ConfigError('Не задан хост базы данных')
if 'user' not in config['Database']:
    raise ConfigError('Не задан пользователь базы данных')
if 'password' not in config['Database']:
    raise ConfigError('Не задан пароль базы данных')
if 'name' not in config['Database']:
    raise ConfigError('Не задано имя базы данных')

database_config = {
    'driver': config['Database']['driver'],
    'host': config['Database']['host'],
    'user': config['Database']['user'],
    'password': config['Database']['password'] if config['Database']['password'] else None,
    'name': config['Database']['name']
}

if 'Storage' not in config:
    raise ConfigError('Не заданы параметры хранилища')
if 'path' not in config['Storage']:
    raise ConfigError('Не задано место хранения загружаемых изображений')

image_storage_config = {
    'path': config['Storage']['path']
}

if 'Gif' not in config:
    raise ConfigError('Не заданы параметры gif')
if 'path' not in config['Gif']:
    raise ConfigError('Не задано место хранения gif')

gif_storage_config = {
    'path': config['Gif']['path']
}

if 'Bot' not in config:
    raise ConfigError('Не заданы параметры бота')

if 'token' not in config['Bot']:
    raise ConfigError('Не задан API TOKEN')

if 'update_method' not in config['Bot']:
    raise ConfigError('Не задан метод получения сообщений')

if 'vlad_username' not in config['Bot']:
    raise ConfigError('Не задан username Влада')

if 'use_proxy' not in config['Bot']:
    raise ConfigError('Не задан параметр использования прокси')

bot_config = {
    'token': config['Bot']['token'],
    'vlad_username': config['Bot']['vlad_username'],
    'use_proxy': config['Bot']['use_proxy'] != 'no',
    'update_method': config['Bot']['update_method']
}

if bot_config['update_method'] == 'webhook':
    if 'webhook_host' not in config['Bot']:
        raise ConfigError('Не задан webhook-хост')
    if 'webhook_port' not in config['Bot']:
        raise ConfigError('Не задан webhook-порт')
    bot_config['webhook_host'] = config['Bot']['webhook_host']
    bot_config['webhook_port'] = config['Bot']['webhook_port']

proxy_config = {}

if bot_config['use_proxy']:
    if 'Proxy' not in config:
        raise ConfigError('Не заданы параметры прокси')
    if 'protocol' not in config['Proxy']:
        raise ConfigError('Не задан протокол прокси')
    if 'host' not in config['Proxy']:
        raise ConfigError('Не задан хост прокси')
    if 'port' not in config['Proxy']:
        raise ConfigError('Не задан порт прокси')
    if 'user' not in config['Proxy']:
        raise ConfigError('Не задан пользователь прокси')
    if 'password' not in config['Proxy']:
        raise ConfigError('Не задан пароль прокси')
    proxy_config = {
        'protocol': config['Proxy']['protocol'],
        'host': config['Proxy']['host'],
        'port': config['Proxy']['port'],
        'user': config['Proxy']['user'],
        'password': config['Proxy']['password'],
    }
