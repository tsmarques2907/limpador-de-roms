@echo off
echo.
echo ======================================================
echo   GERADOR DE EXECUTAVEL - LIMPADOR DE ROMS
echo ======================================================
echo.

:: Substitua 'seu_programa.py' pelo nome real do seu arquivo
set NOME_ARQUIVO=limpador-de-roms.py
:: Substitua 'sonic.ico' pelo nome do seu icone (se houver)
set ICONE=sonic-triggered.ico

echo [1/3] Instalando/Atualizando PyInstaller...
pip install pyinstaller --upgrade

echo.
echo [2/3] Criando o executavel (isso pode levar alguns instantes)...
:: O comando abaixo cria um único arquivo, sem console e com icone
pyinstaller --noconsole --onefile --icon=%ICONE% --clean %NOME_ARQUIVO%

echo.
echo [3/3] Limpando pastas temporarias...
rd /s /q build
del /q *.spec

echo.
echo ======================================================
echo   PROCESSO CONCLUIDO!
echo   O seu .exe esta na pasta 'dist'.
echo ======================================================
pause