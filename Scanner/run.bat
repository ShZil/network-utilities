@echo off
color 0A
title Shzil Network Scanner

REM Check Python version
python --version 2>NUL | findstr /C:"Python 3.10" >NUL
if %errorlevel% neq 0 (
    echo WARNING: Python 3.10 is required to run this script.
    pause
)

REM Reduce console output from kivy (graphical library)
set "KIVY_NO_CONSOLELOG=true"

REM run the python file
python exe.py

REM log the error level of exiting
echo.
echo Process exited with code %errorlevel%.
pause
