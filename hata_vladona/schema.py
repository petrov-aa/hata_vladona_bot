from hata_vladona.hata_vladona import Image
from .configuration import Base, engine


def install():
    Base.metadata.create_all(engine)


def is_installed():
    return engine.dialect.has_table(engine, Image.__tablename__)
