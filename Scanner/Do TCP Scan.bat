@echo off
title TCP Scan
color 0A
:scan
py -c "from scans.TCP import main; main()"
pause
goto scan
