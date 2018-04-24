import os
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError

from hata_vladona.configuration import Session, storage_path
from hata_vladona.models import Image


fetch_url_pattern = 'http://www.stroydom.ru/img/_webcams/cam3_1000x563_%4d-%02d-%02d-%02d.jpg'
fetch_path_pattern = storage_path + '/%04d-%02d-%02d/%02d.jpg'


def __get_current_fetch_date():
    """

    :rtype: datetime
    """
    now = datetime.now()
    return datetime(now.year, now.month, now.day, now.hour)


def __get_fetch_url(date):
    """

    :type date: datetime
    :rtype: str
    """
    return fetch_url_pattern % (date.year, date.month, date.day, date.hour)


def __get_fetch_path(date):
    """

    :type date: datetime
    :rtype: str
    """
    return fetch_path_pattern % (date.year, date.month, date.day, date.hour)


def __check_if_already_fetched(date):
    """

    :type date: datetime
    """
    return Session().query(Image).filter(Image.date == date).first() is not None


def __make_storage_dirs(path):
    """

    :type path: str
    """
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs):
        os.makedirs(dirs)


def fetch_next():

    session = Session()

    try:

        fetch_date = __get_current_fetch_date()

        if __check_if_already_fetched(fetch_date):
            return

        fetch_url = __get_fetch_url(fetch_date)
        fetch_path = __get_fetch_path(fetch_date)

        __make_storage_dirs(fetch_path)

        urllib.request.urlretrieve(fetch_url, fetch_path)

        image = Image(date=fetch_date, path=os.path.abspath(fetch_path))
        session.add(image)

    except (HTTPError, URLError, OSError):

        session.rollback()

    else:

        session.commit()
