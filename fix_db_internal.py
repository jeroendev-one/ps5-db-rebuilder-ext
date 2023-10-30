#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from ftplib import FTP
import sqlite3
import appinfo
import io
import os
from sfo.sfo import SfoFile as SfoFile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("PS5_IP", help="PS5 IP address")
args = parser.parse_args()
appinfo_db = "tmp/appinfo.db"
PS5_IP = args.PS5_IP

if not os.path.exists('tmp'):
    os.makedirs('tmp')

class CUSA:
    sfo = None
    size = 10000000
    is_usable = False

info = {}
files = []

def sort_files(file):
    if "CUSA" in file:
        files.append("'%s'" % file[-9:])

def get_game_info_by_id(GameID):
    if GameID not in info:
        info[GameID] = CUSA()

        buffer = io.BytesIO()
        remote_path = f'/system_data/priv/appmeta/{GameID}'

        try:
            ftp.cwd(remote_path)
            ftp.retrbinary("RETR param.sfo", buffer.write)
            buffer.seek(0)
            sfo = SfoFile.from_reader(buffer)

            info[GameID].sfo = sfo
            info[GameID].size = 100000
            info[GameID].is_usable = True
        except Exception as e:
            print(f"Failed to fetch metadata for {GameID}: {e}")
            return None

    return info[GameID]



ftp = FTP()
ftp.connect(PS5_IP, 1337, timeout=30)
ftp.login(user='username', passwd='password')
if len(files) == 0:
    ftp.cwd('/user/app')
    ftp.dir(sort_files)
    print(files)
    print(' ')
    print(' ')

conn = sqlite3.connect(appinfo_db)
cursor = conn.cursor()
 
for file in files:
    titleid = file[1:-1]  # Extract titleid from the filename, excluding the single quotes
    cursor.execute("SELECT titleid FROM tbl_appinfo WHERE titleid = ?;", (titleid,))
    existing_entry = cursor.fetchone()
    if not existing_entry:
        info = get_game_info_by_id(titleid)  # Use GameID
        if info:
            sql_items = appinfo.get_pseudo_appinfo(info.sfo, info.size)
            for key, value in sql_items.items():
                cursor.execute("INSERT INTO tbl_appinfo (titleid, metadataid, key, val) VALUES (?, ?, ?, ?);", [titleid, "prior:internal:0", key, value])
            print(f"Completed {titleid} - New entry added")
        else:
            print(f"Metadata not found for {titleid}")
    elif existing_entry:
        print(f"Skipped {titleid} - Already exists in the database")


conn.commit()
conn.close()

ftp.close()

