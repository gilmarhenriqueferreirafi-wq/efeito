# -*- coding: utf-8 -*-
"""Gera um .bat por efeito. Rode: python gerar_cmds.py"""
import os

DIR = "Efeitos"
PRE = """@echo off
chcp 65001 >nul
title %s
mode con cols=170 lines=50
:: fonte Consolas (o bloco cheio precisa dela)
reg add "HKCU\\Console\\%%SystemRoot%%_System32_conhost.exe" /v FaceName /t REG_SZ /d "Consolas" /f >nul 2>&1
reg add "HKCU\\Console\\%%SystemRoot%%_System32_conhost.exe" /v FontSize /t REG_DWORD /d 16 /f >nul 2>&1
color %s
cd /d "%%~dp0."
echo.
echo   %s
echo.
python esfera.py %s
if errorlevel 1 pause
"""

EFEITOS = [
    # arquivo                      titulo                              cor  argumentos
    ("01 Azul.cmd",              "ESFERAS - AZUL",                   "1F",  '1 --cores "#1278ff"'),
    ("02 Vermelho.cmd",          "ESFERAS - VERMELHO",               "4F",  '1 --cores "#ff2b2b"'),
    ("03 Verde.cmd",             "ESFERAS - VERDE",                  "2F",  '1 --cores "#2bff6a"'),
    ("04 Ambar.cmd",             "ESFERAS - AMBAR",                  "eF",  '1 --cores "#ffbe28"'),
    ("05 Violeta.cmd",           "ESFERAS - VIOLETA",                "5F",  '1 --cores "#a05aff"'),
    ("06 Branco.cmd",            "ESFERAS - BRANCO",                 "f8",  '1 --cores "#ffffff"'),
    ("10 Cor cheia.cmd",         "ESFERAS - COR CHEIA SEM SOMBRA",   "6F",  '1 --cor-cheia'),
    ("11 Duas cores.cmd",        "ESFERAS - DUAS CORES",             "2F",  '2 --cores "#ff2d2d,#2df0ff"'),
    ("12 Quatro esferas.cmd",    "ESFERAS - QUATRO",                 "5F",  '4'),
    ("20 Metaball.cmd",          "ESFERAS - FUSAO",                  "3F",  '3 --metaball'),
    ("21 Metaball fogo.cmd",     "ESFERAS - FUSAO FOGO",             "eF",  '4 --metaball --cores "#ff3d00,#ffb300,#ff0066"'),
    ("22 Metaball oceano.cmd",   "ESFERAS - FUSAO OCEANO",           "1F",  '5 --metaball --cores "#00e5ff,#1278ff,#3cf0c8"'),
    ("30 Fundo preto.cmd",       "ESFERAS - FUNDO PRETO",            "0F",  '2 --fundo preto'),
    ("31 Chuva.cmd",             "ESFERAS - CHUVA",                  "0A",  '2 --fundo chuva --cores "#00ff66"'),
    ("40 Menu.cmd",              "ESFERAS - MENU",                   "bF",  ''),
]

os.makedirs(DIR, exist_ok=True)
for nome, titulo, cor, args in EFEITOS:
    open(os.path.join(DIR, nome), "w", encoding="mbcs").write(PRE % (titulo, cor, titulo, args))
print("%d efeitos criados em %s\\" % (len(EFEITOS), DIR))
