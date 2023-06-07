@echo off
color 0A
title Network Scanner

REM Check Python version
python --version 2>NUL | findstr /C:"Python 3.10" >NUL
if %errorlevel% neq 0 (
    echo WARNING: Python 3.10 is required to run this script.
    pause
)

REM Suppress console output from kivy (graphical library)
set "KIVY_NO_CONSOLELOG=true"
REM Prevent "OpenGL 1.1 is not good, need OpenGL 2" errors
set KIVY_GL_BACKEND=angle_sdl2

REM run the python file
python exe.py

REM rem log the error level of exiting
echo.
echo Process exited with code %errorlevel%.
pause
