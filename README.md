## Запуск

NOTE: При первом запуске лучше всего закомментировать сервис бота потому что БД будет долго инициализироваться

1. Скопировать config_template.ini в config.ini и заполнить

2. В терминале выполнить
```bash
docker-compose up -d
```

3. Добавить в таблицу image камеру с id=3 (там хардкод на эту камеру по умолчанию, который надо убрать)

После этого боту можно писать `/start`
