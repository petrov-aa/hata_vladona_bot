#!/usr/bin/python3

from hata_vladona.fetcher import fetcher
from hata_vladona import schema

if not schema.is_installed():
    schema.install()

fetcher.fetch_next()
