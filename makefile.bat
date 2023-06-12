@echo off

set root=C:\Users\ultservi\Anaconda3\Scripts
call %root%\activate.bat


cd "src/"

:: C:\Users\ultservi\Anaconda3\python.exe "./src/main.py"
C:\Users\ultservi\Anaconda3\python.exe "main.py"

timeout /t 1


pause