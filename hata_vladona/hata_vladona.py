from sqlalchemy import Column, Integer, DateTime
from .configuration import Base


class Image(Base):

    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)

