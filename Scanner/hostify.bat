@echo off
color 0A

REM if there's no command line argument, go to the `empty` label.
if [%1]==[] goto empty

:assign
REM if there is a command line argument, put its value in %address%
set address=%1
goto body

:empty
REM asks the user to input an IP address, store answer in %address%
set /p "address=Enter IP Address: "

:body
REM method 1 calls `nslookup %address%` and selects only the line which starts with "Name:".
echo Method 1: NSLOOKUP
FOR /F "Tokens=1,* Delims==" %%A in (
    'nslookup %address% ^| FINDSTR "Name:"'
) DO (echo %%A)

echo.
REM method 2 calls this Python snippet which imports socket and calls socket.gethostbyaddr('%address%')
echo Method 2: Python.Socket.GetHostByAddr
py -c "import socket; print('Name:    ' + socket.gethostbyaddr('%address%')[0])"

pause
