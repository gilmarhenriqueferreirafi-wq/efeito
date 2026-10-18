@echo off
chcp 65001 >nul
title ESFERAS - VERDE
mode con cols=170 lines=50
:: fonte Consolas (o bloco cheio precisa dela)
reg add "HKCU\Console\%SystemRoot%_System32_conhost.exe" /v FaceName /t REG_SZ /d "Consolas" /f >nul 2>&1
reg add "HKCU\Console\%SystemRoot%_System32_conhost.exe" /v FontSize /t REG_DWORD /d 16 /f >nul 2>&1
color 2F
cd /d "%~dp0."
echo.
echo   ESFERAS - VERDE
echo.
python esfera.py 1 --cores "#2bff6a"
if errorlevel 1 pause
