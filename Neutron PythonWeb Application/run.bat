@echo off
color 0A
title Neutron Python-Web Application
REM py main.py
pyinstaller main.py --onefile --add-data="index.html;." --add-data="main.css;."
"./dist/main.exe"
pause
