#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Requirements
from ftplib import FTP
from sfo.sfo import SfoFile as SfoFile
import sqlite3
import io
import os
import argparse

## Argparse
parser = argparse.ArgumentParser()
parser.add_argument("PS5_IP", help="PS5 IP address")
args = parser.parse_args()

## Variables
PS5_IP = args.PS5_IP
ftp_port = 1337
ps5_db_folder = '/system_data/priv/mms/'
files = []
info = {}

# CUSA class
class CUSA :
	sfo = None
	size = 10000000
	is_usable = False

# Sort only CUSA files
def sort_files(file) :
	if("CUSA" in file) :
		files.append("'%s'" % file[-9:])

# Use SFO to open param.sfo
def get_game_info_by_id(GameID) :
	if(GameID not in info) :
		info[GameID] = CUSA()

		buffer = io.BytesIO()
		ftp.cwd('/system_data/priv/appmeta/%s/' % GameID)
		ftp.retrbinary("RETR param.sfo" , buffer.write)
		buffer.seek(0)
		sfo = SfoFile.from_reader(buffer)
		info[GameID].sfo = sfo
		#info[GameID].size = ftp.size("/user/app/%s/app.pkg" % GameID)
		info[GameID].is_usable = True

	return info[GameID]

# Directory names to create
dirs_to_create = ['tmp', 'backup']

# Create directories if they don't exist
for directory in dirs_to_create:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"INFO:: Created '{directory}' directory")
    else:
        print(f"INFO:: '{directory}' directory already exists")

# Start FTP connection
ftp = FTP()
ftp.connect(PS5_IP, ftp_port, timeout=30)
ftp.login(user='username', passwd = 'password')

# List of DB files to copy to temporary folder
files_to_copy = ['app.db', 'appinfo.db']
for file_name in files_to_copy:
    print(f"INFO:: Copying file: {file_name} from {ps5_db_folder}")
    try:
        ftp.cwd(ps5_db_folder)
        lf = open(dirs_to_create[0] + '/' + file_name, "wb")
        ftp.retrbinary(f"RETR {file_name}", lf.write)
        lf.close()
    except Exception as e:
        print(f"ERROR:: Error copying {file_name}: {str(e)}")

# Create list of games on the system that are (probably) missing
## If external, change to /mnt/ext0/user/app or /mnt/ext1/user/app
if len(files) == 0:
    ftp.cwd('/user/app/')
    ftp.dir(sort_files)
    print(' ')
    print("Games found in /user/app:")
    print(' ')
    for file in files:
        GameID = file.replace("'", "")
        cusa = get_game_info_by_id(GameID)
        print(cusa.sfo['TITLE_ID'] + ' - ' + cusa.sfo['TITLE'])
 



