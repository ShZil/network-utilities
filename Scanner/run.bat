@echo off
color 0A
title Shzil Network Scanner
python -m exe %*
REM pause
set "KIVY_NO_CONSOLELOG=true"
