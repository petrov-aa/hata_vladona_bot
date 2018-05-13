from datetime import datetime
from sqlalchemy.exc import DatabaseError

from hata_vladona.config import config
from hata_vladona.database import flush_session
from hata_vladona.models import Image, Gif, Camera, GIF_PAST_DAY, GIF_PAST_WEEK, GIF_PAST_MONTH

gif_storage_path = config['Gif']['path']


def get_latest_image(camera):
    """

    :type camera: Camera
    :rtype: Image
    """
    with flush_session() as session:
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
    with flush_session() as session:
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
            return None
        return gif


def __check_if_gif_exists(camera, date, gif_type):
    """

    :rtype: Gif
    :type camera: Camera
    :type date: datetime
    :type gif_type: str
    """
    with flush_session() as session:
        camera = session.merge(camera)
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


def get_past_week_gif(camera):
    """

    :type camera: Camera
    :rtype: Gif
    """
    now = datetime.now()
    date = datetime(now.year, now.month, now.day)
    return __check_if_gif_exists(camera, date, GIF_PAST_WEEK)


def get_today_images(camera):
    """

    :rtype: list(Image)
    :type camera: Camera
    """
    return Image.get_today_images(camera)


def get_image_by_date(camera, date):
    """

        :rtype: Image
        :type camera: Camera
        """
    return Image.get_by_date(camera, date)
