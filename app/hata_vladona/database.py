from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import database_config

__engine_url = URL(database_config['driver'])
__engine_url.username = database_config['user']
__engine_url.password = database_config['password']
__engine_url.host = database_config['host']
__engine_url.database = database_config['name']

engine_url = str(__engine_url)

__engine = create_engine(str(__engine_url) + '?charset=utf8', pool_pre_ping=True)

__Session = scoped_session(sessionmaker(bind=__engine))


@contextmanager
def get_flush_session():
    session = __Session()
    try:
        yield session
        session.flush()
    except:
        session.rollback()
        raise


def flush_session(func):
    def decorated(*args, **kwargs):
        with get_flush_session() as session:
            return func(*args, session=session, **kwargs)
    return decorated


@contextmanager
def get_commit_session():
    session = __Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        __Session.remove()


def commit_session(func):
    def decorated(*args, **kwargs):
        with get_commit_session() as session:
            return func(*args, **kwargs, session=session)
    return decorated


Base = declarative_base()

