from contextlib import contextmanager
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

__Session = scoped_session(sessionmaker(bind=__engine))


@contextmanager
def flush_session():
    session = __Session()
    try:
        yield session
        session.flush()
    except:
        session.rollback()
        # raise


@contextmanager
def commit_session():
    session = __Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        # raise
    finally:
        session.close()


Base = declarative_base()

