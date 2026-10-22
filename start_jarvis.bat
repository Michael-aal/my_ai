@echo off
cd /d C:\Users\HP\Documents\my_ai
echo ===== Jarvis started %date% %time% ===== > jarvis.log
:loop
python -u main.py >> jarvis.log 2>&1
echo [%date% %time%] exited, restarting in 5s... >> jarvis.log
timeout /t 5 /nobreak >nul
goto loop
