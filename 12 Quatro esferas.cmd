@echo off
chcp 65001 >nul
title ESFERAS - QUATRO
mode con cols=170 lines=50
:: fonte Consolas (o bloco cheio precisa dela)
reg add "HKCU\Console\%SystemRoot%_System32_conhost.exe" /v FaceName /t REG_SZ /d "Consolas" /f >nul 2>&1
reg add "HKCU\Console\%SystemRoot%_System32_conhost.exe" /v FontSize /t REG_DWORD /d 16 /f >nul 2>&1
color 5F
cd /d "%~dp0."
echo.
echo   ESFERAS - QUATRO
echo.
python esfera.py 4
if errorlevel 1 pause
