from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from .config import database_config

__engine_url = URL(database_config['driver'])
__engine_url.username = database_config['user']
__engine_url.password = database_config['password']
__engine_url.host = database_config['host']
__engine_url.database = database_config['name']

engine_url = str(__engine_url)

__engine = create_engine(str(__engine_url) + '?charset=utf8')


class __Database:

    __session = None

    def __init__(self, session_maker):
        """

        :type session_maker: sessionmaker
        """
        self.__session__maker = session_maker

    def get_session(self):
        """

        :rtype: Session
        """
        if self.__session is None or self.__session.dirty:
            self.__session = self.__session__maker()
        return self.__session


database = __Database(sessionmaker(bind=__engine))

Base = declarative_base()

