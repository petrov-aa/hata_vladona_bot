import telebot
from aiohttp import web

from hata_vladona.bot import bot
from hata_vladona.config import bot_config

if __name__ == '__main__':

    if bot_config['update_method'] == 'pooling':

        bot.remove_webhook()
        bot.polling(none_stop=True, timeout=9999)

    elif bot_config['update_method'] == 'webhook':

        external_ip = bot_config['webhook_host']
        external_port = int(bot_config['webhook_port'])

        ssl_cert = bot_config['public_cert_path']

        webhook_url_base = 'https://{}:{}'.format(external_ip, external_port)
        webhook_url_path = '/hata_vladona/{}/'.format(bot_config['token'])

        app = web.Application()

        async def handle(request):
            if request.match_info.get('token') == bot.token:
                request_body_dict = await request.json()
                update = telebot.types.Update.de_json(request_body_dict)
                bot.process_new_updates([update])
                return web.Response()
            else:
                return web.Response(status=403)


        app.router.add_post('/{token}/', handle)

        bot.remove_webhook()
        bot.set_webhook(url=webhook_url_base + webhook_url_path,
                        certificate=open(ssl_cert, 'r'))

        web.run_app(
            app,
            path=bot_config['socket_path']
        )

