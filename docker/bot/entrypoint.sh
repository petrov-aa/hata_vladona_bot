#!/bin/sh

# Ждем старта mysql
sleep 10

# Выполяем миграции
alembic upgrade head

# Запускаем службы
/usr/bin/supervisord -c /app/supervisord.conf
