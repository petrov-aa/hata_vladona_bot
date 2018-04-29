from sqlalchemy.exc import DatabaseError

import hata_vladona.configuration.session
from hata_vladona.models import *


def get_latest_image(camera):
    """

    :type camera: Camera
    :rtype: Image
    """
    return session.query(Image).filter(Image.camera_id == camera.id).order_by(Image.date.desc()).first()


def create_past_day_gif(camera):
    """

    :type camera: Camera
    :rtype: Gif
    """
    return __create_gif(camera, GIF_PAST_DAY)


def create_past_week_gif(camera):
    """

    :type camera: Camera
    :rtype: Gif
    """
    return __create_gif(camera, GIF_PAST_WEEK)


def create_past_month_gif(camera):
    """

    :type camera: Camera
    :rtype: Gif
    """
    return __create_gif(camera, GIF_PAST_MONTH)


def __create_gif(camera, gif_type):
    """

    :type camera: Camera
    :type gif_type: str
    :rtype: Gif
    """

    try:
        now = datetime.now()
        date = datetime(now.year, now.month, now.day)
        gif = __check_if_gif_exists(camera, date, gif_type)
        if gif is not None:
            return gif
        gif = Gif()
        gif.camera = camera
        gif.type = gif_type
        gif.date = date
        session.add(gif)
    except DatabaseError:
        session.rollback()
        return None
    else:
        session.commit()
        return gif


def __check_if_gif_exists(camera, date, gif_type):
    """

    :rtype: Gif
    :type camera: Camera
    :type date: datetime
    :type gif_type: str
    """
    return session.query(Gif).filter(Gif.camera_id == camera.id,
                                       Gif.date == date,
                                       Gif.type == gif_type).first()


def get_past_day_gif(camera):
    """

    :type camera: Camera
    :rtype: Gif
    """
    now = datetime.now()
    date = datetime(now.year, now.month, now.day)
    return __check_if_gif_exists(camera, date, GIF_PAST_DAY)
