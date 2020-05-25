import schedule
import time

from hata_vladona import fetcher


def job():
    fetcher.fetch_next()


if __name__ == '__main__':

    schedule.every(30).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
