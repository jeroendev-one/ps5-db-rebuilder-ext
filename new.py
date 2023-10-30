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

## Create temp dir
if not os.path.exists('tmp'):
    os.makedirs('tmp')
    print("INFO:: Created tmp dir")
else:
    print("INFO:: tmp dir already exists")

## Get files list from FTP
ftp = FTP()
ftp.connect(PS5_IP, 1337, timeout=30)
ftp.login(user='username', passwd = 'password')
if(len(files) == 0) :
        ftp.cwd('/user/app/')
        ftp.dir(sort_files)
        print(files)


