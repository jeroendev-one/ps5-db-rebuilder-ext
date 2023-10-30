# ps5-db-rebuilder-ext
PS5 DB Rebuilder for external (M.2 and Ext. USB)

## What it does (Work in progress)
This script connects via FTP and retrieves `app.db` and `appinfo.db` from the PS5 and copies them to a local directory called `tmp` which the script creates.
It checks via FTP if there are games in `/user/app`, or other locations which you are probably missing after a database rebuild. 
After retrieving a list of games from the filesystem, it will compare this list to the values in the PS5 database(s). If some are missing, it will fill the table(s)

To be continued. I need to sleep
