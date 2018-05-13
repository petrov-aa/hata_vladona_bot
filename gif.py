from hata_vladona import export
from hata_vladona.database import commit_session
from hata_vladona.models import Camera

if __name__ == '__main__':
    with commit_session() as session:
        cameras = session.query(Camera).all()
        for camera in cameras:

            gif = export.create_past_day_gif(camera)
            gif = session.merge(gif)
            gif.create_file()

            gif = export.create_past_week_gif(camera)
            gif = session.merge(gif)
            gif.create_file()
