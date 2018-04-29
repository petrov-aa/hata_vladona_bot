from hata_vladona import export
from hata_vladona.configuration import session
from hata_vladona.models import Camera

if __name__ == '__main__':
    cameras = session.query(Camera).all()
    for camera in cameras:
        gif = export.create_past_day_gif(camera)
        gif.create_file()
