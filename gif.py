from hata_vladona import export
from hata_vladona.database import get_commit_session
from hata_vladona.models import Camera

if __name__ == '__main__':

    with get_commit_session() as session:

        cameras = session.query(Camera).all()

        for camera in cameras:

            gif = export.create_past_day_gif(camera)
            gif.create_file()

            gif = export.create_past_week_gif(camera)
            gif.create_file()

            gif = export.create_past_month_gif(camera)
            gif.create_file()
