@echo off
color 0A
title Neutron Python-Web Application
REM py main.py
pyinstaller main.py --noconsole --onefile --add-data="index.html;." --add-data="main.css;."
pause
