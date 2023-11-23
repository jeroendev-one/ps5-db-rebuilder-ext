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
import subprocess

## Argparse
parser = argparse.ArgumentParser()
parser.add_argument("PS5_IP", help="PS5 IP address")
parser.add_argument("EXT_DISK", choices=["ext0", "ext1"], help="External interface (ext0 or ext1)")
args = parser.parse_args()

## Variables
PS5_IP = args.PS5_IP
EXT_DISK = args.EXT_DISK
ftp_port = 2121
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
		ftp.cwd('/system_data/priv/appmeta/external/%s/' % GameID)
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


# List of DB files to copy to a folder named "backup"
files_to_copy = {
    'app.db': '/system_data/priv/mms',
    'appinfo.db': '/system_data/priv/mms',
    'concept_title.db': '/system/priv/mms_ro'
}

for file_name, remote_path in files_to_copy.items():
    local_file_path = os.path.join(dirs_to_create[0], file_name)

    # Check if the file exists and is a regular file
    with open(local_file_path, 'wb') as local_file:
        ftp.cwd(remote_path)
        ftp.retrbinary(f'RETR {file_name}', local_file.write)
    print(f"File {file_name} downloaded successfully.")


# Create list of games on the system that are (probably) missing
## If external, change to /mnt/ext0/user/app or /mnt/ext1/user/app
ftp.cwd(app_dir)
ftp.dir(sort_files)
if len(files) > 0:
    print(f"\n{info_msg} Titles found in {app_dir}:\n")
    for file in files:
        GameID = file.replace("'", "")
        game = get_game_info_by_id(GameID)
        print(game.sfo['TITLE_ID'] + ' - ' + game.sfo['TITLE'])
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
        GameID = title[0]
        game = get_game_info_by_id(GameID)
            
        print(game.sfo['TITLE_ID'] + ' - ' + game.sfo['TITLE'])

# Convert the list of titles into sets while removing single quotes
files_set = set(title.strip("'") for title in files)
titles_appinfo_set = set(title[0].strip("'") for title in titles_appinfo)

# Find titles in files_set that are not in titles_appinfo_set
missing_titles = files_set - titles_appinfo_set

# Print the missing titles
if len(missing_titles) > 0:

    print(f"\n{info_msg} Titles in {app_dir} but not in the database:")
    for title in missing_titles:
        GameID = title.replace("'", "")
        game = get_game_info_by_id(GameID)
        print(game.sfo['TITLE_ID'] + ' - ' + game.sfo['TITLE'])

elif len(missing_titles) == 0:
    print(f"\n{info_msg} All titles in {app_dir} are also in the database.")

## Now really fixing the issues
if len(missing_titles) > 0:
    print(f"\n----------------------------")
    print("Starting to process missing title ID's")
    print(f"----------------------------\n")
    for title in missing_titles:
        GameID = title.replace("'", "")
        game = get_game_info_by_id(GameID)
        cusa = game.sfo['TITLE_ID']
        title = game.sfo['TITLE']
        version = game.sfo['VERSION']
        content_id = game.sfo['CONTENT_ID']
        print(f"Processing: {cusa} - {title}")

        # Try to get concept ID from concept_title.db
        conn = sqlite3.connect(dirs_to_create[0] + '/' + "concept_title.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT concept_id FROM tbl_concept_title WHERE title_id = ?", (cusa,))
        result = cursor.fetchone()

        if result:
            concept_id = result[0]
            print(f"Concept ID for title ID {cusa} is: {concept_id}")
        else:
            print(f"Concept ID not found. Setting to 0")
            concept_id = '0'
        #print(concept_id)


        # Import huge dict
        from appinfo_dict import data_lines

        data_to_insert = []

        for line in data_lines:
            line = line.format(cusa=cusa, title=title, version=version, content_id=content_id)
            parts = line.split(' ')
            metaDataId = parts[0]
            key = parts[1]
            val = ' '.join(parts[2:]) if len(parts) > 2 else ''  # Concatenate the rest as 'val'

            data_entry = {
                'titleid': cusa,
                'metaDataId': metaDataId,
                'key': key,
                'val': val
            }
            data_to_insert.append(data_entry)

        # Display the resulting list of dictionaries
        #for entry in data_to_insert:
            #print(entry)

        # Create a connection to the database
        conn = sqlite3.connect(dirs_to_create[0] + '/' + "appinfo.db")
        cursor = conn.cursor()

        # Define SQL query for insertion
        sql_query = "INSERT INTO tbl_appinfo (titleid, metaDataId, key, val) VALUES (?, ?, ?, ?)"

        # Prepare data for insertion
        data_to_insert_values = [(entry['titleid'], entry['metaDataId'], entry['key'], entry['val']) for entry in data_to_insert]

        # Execute the insertion query using executemany()
        cursor.executemany(sql_query, data_to_insert_values)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()