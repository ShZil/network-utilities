@echo off
color 0A

REM if there's no command line argument, go to the `empty` label.
if [%1]==[] goto empty

:assign
REM if there is a command line argument, put its value in %address%
set address=%*
goto body

:empty
REM asks the user to input an IP address, store answer in %address%
set /p "address=Enter IP Address: "
echo.

:body
echo.

(for %%a in (%address%) do (
    REM method 1 calls `nslookup %address%` and selects only the line which starts with "Name:".
    echo --- %%a ---
    echo Method 1: C:\Windows\System32\nslookup.exe
    FOR /F "Tokens=1,* Delims==" %%A in (
        'nslookup %%a ^| FINDSTR "Name:"'
    ) DO (echo %%A)

    echo.
    REM method 2 calls this Python snippet which imports socket and calls socket.gethostbyaddr('%address%')
    echo Method 2: Python.Socket.GetHostByAddr
    py -c "import socket; print('Name:    ' + socket.gethostbyaddr('%%a')[0])"

    echo.
    echo.
))


pause
