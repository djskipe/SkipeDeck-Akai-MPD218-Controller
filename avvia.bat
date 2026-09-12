@echo off
:: Rilevamento privilegi di amministratore
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Richiesta dei privilegi di amministratore...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

:: Riporta la directory di lavoro a quella del file .bat
cd /d "%~dp0"

title MIDI SkipeDeck - Setup e Avvio

echo ========================================
echo    MIDI SkipeDeck - Setup e Avvio
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

    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP%\python-3.12.0-installer.exe'"

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

    "%TEMP%\python-3.12.0-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=1 InstallLauncherAllUsers=1

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
    del /f /q "%TEMP%\python-3.12.0-installer.exe" >nul 2>&1
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
echo - keyboard
echo.

python -m pip install --upgrade pip --quiet

if errorlevel 1 (
    echo [ERRORE] Aggiornamento pip fallito.
    pause
    exit /b 1
)

python -m pip install pygame pyautogui pillow pynput --quiet

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
:: CONVERSIONE PNG -> ICO MULTI-RISOLUZIONE
:: ========================================

set "PNG=%~dp0skipedeck.png"
set "ICONA=%~dp0skipedeck.ico"

if exist "%PNG%" (
    echo Conversione icona PNG -^> ICO multi-risoluzione...

    python -c "from PIL import Image; img = Image.open(r'%PNG%'); img.save(r'%ICONA%', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"

    if errorlevel 1 (
        echo [WARN] Conversione icona fallita, uso icona di default.
    ) else (
        echo [OK] Icona multi-risoluzione creata.
    )
) else (
    if exist "%ICONA%" (
        echo [INFO] PNG non trovato, uso il file ICO esistente.
    ) else (
        echo [WARN] Ne' PNG ne' ICO trovati, icona di default.
    )
)

:: ========================================
:: CREAZIONE ICONA SUL DESKTOP
:: ========================================

echo Creazione icona sul desktop...

set "SCRIPT=%~dp0midi_streamdeck.py"
set "LINK=%USERPROFILE%\Desktop\MIDI SkipeDeck.lnk"

:: Trova pythonw.exe (versione senza console)
set "PYTHONW="
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW set "PYTHONW=%%i"
)

:: Se non trovato, prova nel path standard di Python 3.12
if not defined PYTHONW (
    if exist "%ProgramFiles%\Python312\pythonw.exe" (
        set "PYTHONW=%ProgramFiles%\Python312\pythonw.exe"
    )
)

if not defined PYTHONW (
    echo [WARN] pythonw.exe non trovato, salto la creazione dell'icona.
    goto :avvio
)

if not exist "%ICONA%" (
    echo [WARN] File icona non trovato: %ICONA%
    echo        L'icona usera' quella di default di Python.
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%LINK%'); $sc.TargetPath = '%PYTHONW%'; $sc.Arguments = '\"%SCRIPT%\"'; $sc.WorkingDirectory = '%~dp0'; if (Test-Path '%ICONA%') { $sc.IconLocation = '%ICONA%' }; $sc.Description = 'MIDI SkipeDeck'; $sc.Save()"

if exist "%LINK%" (
    echo [OK] Icona creata sul desktop: MIDI SkipeDeck
) else (
    echo [WARN] Impossibile creare l'icona sul desktop.
)

:avvio

:: ========================================
:: AVVIO MIDI SKIPEDECK
:: ========================================

echo.
echo ========================================
echo       AVVIO MIDI SKIPEDECK
echo ========================================
echo.

python midi_streamdeck.py

echo.
echo ========================================
echo       MIDI SkipeDeck terminato
echo ========================================
echo.

pause