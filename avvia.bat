@echo off
setlocal EnableExtensions
title MIDI StreamDeck - Setup e Avvio

echo ========================================
echo    MIDI StreamDeck - Setup e Avvio
echo ========================================
echo.

:: ========================================
:: CONTROLLO PYTHON
:: ========================================

python --version >nul 2>&1

if errorlevel 1 (
    echo [INFO] Python non trovato.
    echo.
    echo Download di Python 3.12.0...

    set "PYTHON_INSTALLER=%TEMP%\python-3.12.0-installer.exe"

    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"

    if errorlevel 1 (
        echo.
        echo [ERRORE] Impossibile scaricare Python 3.12.0.
        pause
        exit /b 1
    )

    echo [OK] Python 3.12.0 scaricato.
    echo.
    echo Installazione di Python 3.12.0...
    echo.

    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

    if errorlevel 1 (
        echo.
        echo [ERRORE] Installazione di Python fallita.
        pause
        exit /b 1
    )

    echo [OK] Python 3.12.0 installato.
    echo.

    :: Aggiorna il PATH della sessione corrente
    set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"

    :: Rimuove installer temporaneo
    del /f /q "%PYTHON_INSTALLER%" >nul 2>&1
)

:: ========================================
:: VERIFICA PYTHON
:: ========================================

echo [OK] Python trovato:
python --version
echo.

:: ========================================
:: VERIFICA PIP
:: ========================================

python -m pip --version >nul 2>&1

if errorlevel 1 (
    echo [INFO] Pip non trovato. Installazione...
    python -m ensurepip --upgrade
)

:: ========================================
:: INSTALLAZIONE DIPENDENZE
:: ========================================

echo.
echo Installazione dipendenze:
echo - pygame
echo - pyautogui
echo - pillow
echo.

python -m pip install --upgrade pip --quiet

if errorlevel 1 (
    echo [ERRORE] Aggiornamento pip fallito.
    pause
    exit /b 1
)

python -m pip install pygame pyautogui pillow --quiet

if errorlevel 1 (
    echo.
    echo [ERRORE] Installazione delle dipendenze fallita.
    pause
    exit /b 1
)

echo.
echo [OK] Dipendenze installate correttamente.
echo.

:: ========================================
:: AVVIO MIDI STREAMDECK
:: ========================================

echo ========================================
echo       AVVIO MIDI STREAMDECK
echo ========================================
echo.

python midi_streamdeck.py

echo.
echo ========================================
echo       MIDI StreamDeck terminato
echo ========================================
echo.

pause