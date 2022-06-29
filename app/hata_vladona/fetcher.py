import os
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError
from sqlalchemy.orm import Session

from hata_vladona.database import commit_session, flush_session
from hata_vladona.models import Image, Camera


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
    if camera.url_as_is:
        return camera.url_base
    # -1 взят с прода
    return camera.url_base % (date.year, date.month, date.day, date.hour-1)


@flush_session
def __check_if_already_fetched(camera, date, session=None):
    """

    :type session: Session
    :type camera: Camera
    :type date: datetime
    """
    return session.query(Image).filter(Image.camera_id == camera.id,
                                       Image.date == date).first() is not None


def __make_storage_dirs(path):
    """

    :type path: str
    """
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs):
        os.makedirs(dirs)


@commit_session
def fetch_next(session=None):
    """

    :type session: Session
    """
    try:
        cameras = session.query(Camera).all()

        for camera in cameras:

            fetch_date = __get_current_fetch_date()

            if __check_if_already_fetched(camera, fetch_date):
                return

            image = Image()
            image.date = fetch_date
            image.camera = camera

            fetch_url = __get_fetch_url(camera, fetch_date)
            fetch_path = image.get_file_path()

            __make_storage_dirs(fetch_path)

            if camera.is_mjpeg:
                # todo как-то получить фрейм mjpeg и сохранить его в файл
                raise Exception("Not implemented")
            else:
                urllib.request.urlretrieve(fetch_url, fetch_path)

            session.add(image)

    except (HTTPError, URLError):
        pass
