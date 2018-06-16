#!/bin/bash

ssh hata_vladona@91.235.137.225 "mysqldump hata_vladona > dump.sql"
scp hata_vladona@91.235.137.225:./dump.sql dump.sql
mysql -e "drop database hata_vladona;"
mysql -e "create database hata_vladona default character set utf8 default collate utf8_unicode_ci;"
mysql hata_vladona < dump.sql
rm dump.sql

