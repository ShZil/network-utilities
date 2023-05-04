@echo off
title Refresh scans.db
del scans.db
py db.py
echo Done.
pause
