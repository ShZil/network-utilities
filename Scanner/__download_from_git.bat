@echo off
color 0A
title Clone from Git
if exist "network-utilities\" rmdir /S /Q network-utilities
git clone https://github.com/ShZil/network-utilities.git network-utilities
pause

