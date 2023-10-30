#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Requirements
from ftplib import FTP
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
PORT=1337

# Directory names
base_directory = 'tmp'
sub_directory = 'backup'

# Create the base directory ('tmp') if it doesn't exist
if not os.path.exists(base_directory):
    os.makedirs(base_directory)
    print(f"INFO:: Created '{base_directory}' directory")
else:
    print(f"INFO:: '{base_directory}' directory already exists")

# Create the subdirectory ('backup') inside the base directory
backup_directory = os.path.join(base_directory, sub_directory)
if not os.path.exists(backup_directory):
    os.makedirs(backup_directory)
    print(f"INFO:: Created '{sub_directory}' directory inside '{base_directory}'")
else:
    print(f"INFO:: '{sub_directory}' directory inside '{base_directory}' already exists")

## Get files list from FTP
ftp = FTP()
ftp.connect(PS5_IP, 1337, timeout=30)
ftp.login(user='username', passwd = 'password')
if(len(files) == 0) :
        ftp.cwd('/user/app/')
        ftp.dir(sort_files)
        print(files)


