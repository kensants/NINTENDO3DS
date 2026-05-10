@echo off
chcp 65001 > nul
py -V > nul
if %errorlevel% NEQ 0 (
    echo Python 3 no esta instalado.
    echo Instala Python 3 e intentalo de nuevo.
    echo Descargalo desde https://www.python.org/downloads/
    echo.
    pause
    exit
)
py -3 mset9.py