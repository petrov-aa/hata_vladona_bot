FROM python:3.6-alpine

RUN apk add --virtual .build-deps \
    build-base

RUN apk add tzdata && \
    cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    echo "Europe/Moscow" > /etc/timezone

RUN apk add supervisor

# Копируем только файл с зависимостями, чтобы не билдить все заново при правке кода,
# а только при изменении зависимостей
COPY ./app/requirements.txt /app/app/requirements.txt
WORKDIR /app/app
RUN pip install -r requirements.txt

RUN apk del .build-deps

COPY ./docker/bot/entrypoint.sh /run.sh
COPY ./docker/bot/supervisord.conf /app/supervisord.conf
RUN chmod u+x /run.sh

CMD ["/run.sh"]
