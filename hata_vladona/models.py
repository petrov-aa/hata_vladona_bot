import os
import shutil
import subprocess
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .config import gif_storage_config
from .database import database, Base


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
    path = Column(String(255))
    camera_id = Column(Integer, ForeignKey('camera.id'))
    camera = relationship('Camera')

    hour_start = 8
    hour_end = 20

    def get_file_path(self):
        """

        :rtype: str
        """
        return self.path

    @staticmethod
    def get_by_date(camera, date):
        """

        :type camera: Camera
        :param date: datetime
        :return:
        :rtype: Image
        """
        session = database.get_session()
        return session.query(Image).filter(Image.camera_id == camera.id,
                                           Image.date == date).first()

    @staticmethod
    def get_today_images(camera):
        """

        :rtype: list(Image)
        :type camera: Camera
        """
        session = database.get_session()
        now = datetime.now()
        date_from = datetime(now.year, now.month, now.day).replace(hour=Image.hour_start)
        if now.hour < Image.hour_start:
            date_from = date_from - timedelta(days=1)
        return session.query(Image).\
            filter(Image.camera_id == camera.id,
                   Image.date >= date_from).all()


class Gif(Base):

    __tablename__ = 'gif'

    id = Column(Integer, primary_key=True)
    type = Column(String(20))
    date = Column(DateTime)
    file_id = Column(String(255))
    camera_id = Column(Integer, ForeignKey('camera.id'))
    camera = relationship('Camera')

    __file_pattern = gif_storage_config['path'] + '/%d/%s-%04d-%02d-%02d-%02d.gif'
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
        image_list = self.get_image_list()
        index = 0
        self.create_gif_dir()
        Gif.create_tmp_dir()
        for image in image_list:
            if os.path.exists(image.get_file_path()):
                shutil.copyfile(image.get_file_path(), Gif.__tmp_path + '/image%010d.jpg' % index)
                index += 1
        image_path = os.path.abspath(Gif.__tmp_path)
        subprocess.call(['convert',
                         '-loop', '1',
                         '-delay', '25',
                         image_path + '/*.jpg',
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
            return date - timedelta(days=7)
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
    camera_id = Column(Integer, ForeignKey('camera.id'))
    state = Column(String(50))
    camera = relationship('Camera')


class Camera(Base):
    __tablename__ = 'camera'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url_base = Column(String(255))
    images = relationship('Image', cascade='all, delete-orphan')
    gifs = relationship('Gif', cascade='all, delete-orphan')
