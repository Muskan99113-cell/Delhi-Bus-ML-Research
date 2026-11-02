@echo off
REM Delhi city-bus interval prediction - full run on Windows (VS Code terminal or double-click)
REM 1) Unzip Month_1.zip, Month_2.zip, Month_3.zip into the "data" folder so that data\Month_1\425\Day1.xlsx etc. exist.
cd /d "%~dp0"
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
REM Add --skip-train to reuse saved model results (the MLP stage takes ~10+ minutes on one core)
python src\main.py %*
pause
