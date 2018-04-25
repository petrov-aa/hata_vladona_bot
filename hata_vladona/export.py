from sqlalchemy.exc import DatabaseError

from hata_vladona.models import *


def get_latest_image():
    """

    :rtype: Image
    """
    session = Session()
    return session.query(Image).order_by(Image.date.desc()).first()


def create_today_gif():
    """

    :rtype: Gif
    """
    return __create_gif(GIF_TODAY)


def create_past_day_gif():
    """

    :rtype: Gif
    """
    return __create_gif(GIF_PAST_DAY)


def create_past_week_gif():
    """

    :rtype: Gif
    """
    return __create_gif(GIF_PAST_WEEK)


def create_past_month_gif():
    """

    :rtype: Gif
    """
    return __create_gif(GIF_PAST_MONTH)


def __create_gif(gif_type):
    """

    :type gif_type: str
    :rtype: Gif
    """
    session = Session()

    try:
        now = datetime.now()
        date = datetime(now.year, now.month, now.day)
        gif = __check_if_gif_exists(date, gif_type)
        if gif is not None:
            return gif
        gif = Gif()
        gif.type = gif_type
        gif.date = date
        session.add(gif)
    except DatabaseError:
        session.rollback()
        return None
    else:
        session.commit()
        return gif


def __check_if_gif_exists(date, gif_type):
    return Session().query(Gif).filter(Gif.date == date, Gif.type == gif_type).first()


def get_past_day_gif():
    """

    :rtype: Gif
    """
    now = datetime.now()
    date = datetime(now.year, now.month, now.day)
    return __check_if_gif_exists(date, GIF_PAST_DAY)
