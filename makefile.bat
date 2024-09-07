@echo off

set root=C:\Users\ultservi\Anaconda3\Scripts
call %root%\activate.bat


cd "src/"

:: C:\Users\ultservi\Anaconda3\python.exe "./src/gui.py"
C:\Users\ultservi\Anaconda3\python.exe "gui.py"

timeout /t 1


pause