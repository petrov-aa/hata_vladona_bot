from hata_vladona.models import *

if __name__ == '__name__':

    session = Session()

    print(session.query(Image).get(5).get_file_path())
