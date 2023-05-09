@echo off
color 0A
title Shzil Network Scanner
set "KIVY_NO_CONSOLELOG=true"
python exe.py
echo.
echo Process exited with code %errorlevel%.
pause
