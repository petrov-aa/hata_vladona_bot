import os
import shutil
import subprocess
from datetime import datetime, timedelta

import telebot
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship, Session

from .config import gif_storage_config, image_storage_config
from .database import flush_session, Base


GIF_TODAY = 'today'
GIF_PAST_DAY = 'past_day'
GIF_PAST_WEEK = 'past_week'
GIF_PAST_MONTH = 'past_month'

CHAT_STATE_WAIT_TIME = 'wait_time'
CHAT_STATE_WAIT_CAMERA = 'wait_camera'


class Image(Base):

    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    camera_id = Column(Integer, ForeignKey('camera.id'))
    camera = relationship('Camera')

    hour_start = 8
    hour_end = 20

    __file_pattern = '/%d/%04d-%02d-%02d/%02d.jpg'

    def get_file_path(self):
        """

        :rtype: str
        """
        date = self.date
        camera = self.camera
        return image_storage_config['path'] + self.__file_pattern % (camera.id,
                                                                     date.year,
                                                                     date.month,
                                                                     date.day,
                                                                     date.hour)

    @classmethod
    @flush_session
    def get_by_date(cls, camera, date, session=None):
        """

        :type session: Session
        :type camera: Camera
        :param date: datetime
        :return:
        :rtype: Image
        """
        image = session.query(cls).filter(cls.camera_id == camera.id,
                                          cls.date == date).first()
        return image

    @classmethod
    @flush_session
    def get_today_images(cls, camera, session=None):
        """

        :type session: Session
        :rtype: list
        :type camera: Camera
        """
        now = datetime.now()
        date_from = datetime(now.year, now.month, now.day).replace(hour=cls.hour_start)
        if now.hour < cls.hour_start:
            date_from = date_from - timedelta(days=1)
        images = session.query(cls).\
            filter(cls.camera_id == camera.id,
                   cls.date >= date_from).all()
        return images

    @classmethod
    @flush_session
    def get_first_image(cls, camera, session=None):
        return session.query(Image).filter(Image.camera == camera).order_by(Image.date).first()

    @classmethod
    @flush_session
    def get_day_first_image(cls, camera, date, session=None):
        return session.query(cls).filter(Image.camera == camera, Image.date >= date)\
            .order_by(Image.date).first()


class Gif(Base):

    __tablename__ = 'gif'

    id = Column(Integer, primary_key=True)
    type = Column(String(20))
    date = Column(DateTime)
    file_id = Column(String(255))
    camera_id = Column(Integer, ForeignKey('camera.id'))
    camera = relationship('Camera')
    messages = relationship('Message', cascade='all, delete-orphan')

    __file_pattern = gif_storage_config['path'] + '/%d/%s-%04d-%02d-%02d-%02d.mp4'
    __tmp_path = gif_storage_config['path'] + '/tmp'

    def get_file_path(self):
        return Gif.__file_pattern % (self.camera_id,
                                     self.type,
                                     self.date.year,
                                     self.date.month,
                                     self.date.day,
                                     self.date.hour)

    def is_file_exists(self):
        os.path.exists(self.get_file_path())

    @staticmethod
    def create_tmp_dir():
        if not os.path.isdir(Gif.__tmp_path):
            os.makedirs(Gif.__tmp_path)

    @staticmethod
    def remove_tmp_dir():
        if os.path.isdir(Gif.__tmp_path):
            shutil.rmtree(Gif.__tmp_path)

    def create_gif_dir(self):
        gif_dir = os.path.dirname(self.get_file_path())
        if not os.path.isdir(gif_dir):
            os.makedirs(gif_dir)

    def create_file(self):
        image_list_raw = self.get_image_list()
        if self.type == GIF_PAST_MONTH:
            image_list = image_list_raw[::4]
        else:
            image_list = image_list_raw
        index = 0
        self.create_gif_dir()
        Gif.remove_tmp_dir()
        Gif.create_tmp_dir()
        for image in image_list:
            if os.path.exists(image.get_file_path()):
                shutil.copyfile(image.get_file_path(), Gif.__tmp_path + '/image%010d.jpg' % index)
                index += 1
        image_path = os.path.abspath(Gif.__tmp_path)
        subprocess.call(['ffmpeg',
                         '-framerate',
                         '5',
                         '-i',
                         image_path + '/image%010d.jpg',
                         '-c:v',
                         'libx264',
                         '-profile:v',
                         'high',
                         '-crf',
                         '20',
                         '-vf',
                         'scale=trunc(iw/2)*2:trunc(ih/2)*2',
                         '-y',
                         '-pix_fmt',
                         'yuv420p',
                         self.get_file_path()])
        Gif.remove_tmp_dir()

    def get_start_date(self):
        """

        :rtype: datetime
        """
        now = datetime.now()
        date = datetime(now.year, now.month, now.day, Image.hour_start)
        if self.type == GIF_TODAY:
            return date
        elif self.type == GIF_PAST_DAY:
            return date - timedelta(days=1)
        elif self.type == GIF_PAST_WEEK:
            date = date - timedelta(days=7)
            if date < self.camera.start_date:
                return self.camera.start_date
            return date
        elif self.type == GIF_PAST_MONTH:
            return date - timedelta(days=30)
        else:
            raise AttributeError('Неверный период времени')

    def get_end_date(self):
        """

        :rtype: datetime
        """
        now = datetime.now()
        date = datetime(now.year, now.month, now.day, now.hour)
        if self.type == GIF_TODAY:
            return date
        else:
            date = date - timedelta(days=1)
            date = date.replace(hour=Image.hour_end)
            return date

    def get_image_list(self):
        """

        :rtype: list[Image]
        """
        start_date = self.get_start_date()
        end_date = self.get_end_date()

        current_date = start_date
        dt = timedelta(hours=1)

        result = list()

        camera = self.camera

        while current_date <= end_date:
            image = Image.get_by_date(camera, current_date)
            if image is not None:
                result.append(image)
            current_date = current_date + dt

        return result


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(String(32), index=True, unique=True)
    camera_id = Column(Integer, ForeignKey('camera.id'))
    state = Column(String(50))
    camera = relationship('Camera')
    messages = relationship('Message', cascade='all, delete-orphan')

    @staticmethod
    @flush_session
    def get_by_telegram_chat_id(telegram_chat_id, session=None):
        """

        :type session: Session
        :rtype: Chat
        :type telegram_chat_id: int
        """
        return session.query(Chat).\
            filter(Chat.telegram_chat_id == telegram_chat_id).first()


class Camera(Base):
    __tablename__ = 'camera'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url_base = Column(String(255))
    start_date = Column(DateTime)
    images = relationship('Image', cascade='all, delete-orphan')
    gifs = relationship('Gif', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    chat = relationship('Chat')
    telegram_message_id = Column(Integer)
    gif_id = Column(Integer, ForeignKey('gif.id'))
    gif = relationship('Gif')
