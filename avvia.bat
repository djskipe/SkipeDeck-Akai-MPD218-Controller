@echo off
echo ========================================
echo    MIDI StreamDeck - Setup e Avvio
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Scaricalo da: https://www.python.org/downloads/
    echo Assicurati di spuntare "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python trovato:
python --version
echo.

echo Installazione dipendenze (pygame, pyautogui, pillow)...
:: Ho aggiunto 'pillow' alla fine della lista qui sotto
python -m pip install pygame pyautogui pillow --quiet
if errorlevel 1 (
    echo [ERRORE] Installazione fallita.
    pause
    exit /b 1
)

echo [OK] Dipendenze installate correttamente.
echo.
echo Avvio MIDI StreamDeck...
python midi_streamdeck.py

pause