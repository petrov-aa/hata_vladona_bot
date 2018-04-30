import os
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError

from hata_vladona.config import image_storage_config
from hata_vladona.database import database
from hata_vladona.models import Image, Camera

fetch_path_pattern = image_storage_config['path'] + '/%d/%04d-%02d-%02d/%02d.jpg'


def __get_current_fetch_date():
    """

    :rtype: datetime
    """
    now = datetime.now()
    return datetime(now.year, now.month, now.day, now.hour)


def __get_fetch_url(camera, date):
    """

    :type camera: Camera
    :type date: datetime
    :rtype: str
    """
    return camera.url_base % (date.year, date.month, date.day, date.hour)


def __get_fetch_path(camera, date):
    """

    :type camera: Camera
    :type date: datetime
    :rtype: str
    """
    return fetch_path_pattern % (camera.id, date.year, date.month, date.day, date.hour)


def __check_if_already_fetched(camera, date):
    """

    :type camera: Camera
    :type date: datetime
    """
    session = database.get_session()
    return session.query(Image).filter(Image.camera_id == camera.id,
                                       Image.date == date).first() is not None


def __make_storage_dirs(path):
    """

    :type path: str
    """
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs):
        os.makedirs(dirs)


def fetch_next():
    session = database.get_session()
    try:
        cameras = session.query(Camera).all()

        for camera in cameras:

            fetch_date = __get_current_fetch_date()

            if __check_if_already_fetched(camera, fetch_date):
                return

            fetch_url = __get_fetch_url(camera, fetch_date)
            fetch_path = __get_fetch_path(camera, fetch_date)

            __make_storage_dirs(fetch_path)

            urllib.request.urlretrieve(fetch_url, fetch_path)

            image = Image()
            image.date = fetch_date
            image.path = os.path.abspath(fetch_path)
            image.camera = camera

            session.add(image)

    except (HTTPError, URLError, OSError):
        session.rollback()
    else:
        session.commit()
