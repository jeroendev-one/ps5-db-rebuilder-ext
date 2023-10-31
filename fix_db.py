#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Requirements
from ftplib import FTP
from sfo.sfo import SfoFile as SfoFile
import sqlite3
import io
import os
import sys
import argparse

## Argparse
parser = argparse.ArgumentParser()
parser.add_argument("PS5_IP", help="PS5 IP address")
parser.add_argument("EXT_DISK", choices=["ext0", "ext1"], help="External interface (ext0 or ext1)")
args = parser.parse_args()

## Variables
PS5_IP = args.PS5_IP
EXT_DISK = args.EXT_DISK
ftp_port = 1337
ps5_db_folder = '/system_data/priv/mms/'
info_msg = 'INFO::'
error_msg = 'ERROR::'
files = []
info = {}

# Set variables based on parameters {ext0,ext1}
if EXT_DISK == 'ext1':
    app_dir = '/mnt/ext1/user/app'
    print(f"{info_msg} App directory set to {app_dir}")
elif EXT_DISK == 'ext0':
    app_dir = '/mnt/ext0/user/app'
    print(f"{info_msg} App directory set to {app_dir}")

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

# Start FTP connection
ftp = FTP()
ftp.connect(PS5_IP, ftp_port, timeout=30)
ftp.login(user='username', passwd = 'password')

# List of DB files to copy to temporary folder
files_to_copy = ['app.db', 'appinfo.db']
for file_name in files_to_copy:
    print(f"{info_msg} Copying file: {file_name} from {ps5_db_folder}")
    try:
        ftp.cwd(ps5_db_folder)
        lf = open(dirs_to_create[0] + '/' + file_name, "wb")
        ftp.retrbinary(f"RETR {file_name}", lf.write)
        lf.close()
    except Exception as e:
        print(f"{error_msg} Error copying {file_name}: {str(e)}")

# Create list of games on the system that are (probably) missing
## If external, change to /mnt/ext0/user/app or /mnt/ext1/user/app
ftp.cwd(app_dir)
ftp.dir(sort_files)
if len(files) > 0:
    print(f"\n{info_msg} Titles found in {app_dir}:\n")
    for file in files:
        GameID = file.replace("'", "")
        cusa = get_game_info_by_id(GameID)
        print(cusa.sfo['TITLE_ID'] + ' - ' + cusa.sfo['TITLE'])
else:
    print(f"{error_msg} No titles found in {app_dir}")
    sys.exit(1)
 
 ## Get current title id's from tbl_appinfo
conn = sqlite3.connect(dirs_to_create[0] + '/' + "appinfo.db")
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT titleid from tbl_appinfo WHERE titleid like 'CUSA%%';")
titles_appinfo = cursor.fetchall()
if len(titles_appinfo) == 0:
    print(f"\n{info_msg} No CUSA titles found in database. Probably why you are running this script ;)")
else:
    print(f"\n{info_msg} Titles found in database:")
    for title in titles_appinfo:
        print(title[0])

# Convert the lists of titles into sets
files_set = set(files)
titles_appinfo_set = set(title[0] for title in titles_appinfo)

# Find titles in files_set that are not in titles_appinfo_set
missing_titles = files_set - titles_appinfo_set

# Print the missing titles
if len(missing_titles) > 0:
    print(f"\n{info_msg} Titles in {app_dir} but not in the database:")
    for title in missing_titles:
        GameID = title.replace("'", "")
        cusa = get_game_info_by_id(GameID)
        print(cusa.sfo['TITLE_ID'] + ' - ' + cusa.sfo['TITLE'])
elif len(missing_titles) == 0:
    print(f"{info_msg} No titles missing in database which are also in {app_dir}")
else:
    print(f"\n{info_msg} All titles in {app_dir} are also in the database.")






