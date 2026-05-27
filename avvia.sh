#!/bin/bash
echo "========================================"
echo "  MIDI StreamDeck - Setup e Avvio"
echo "========================================"
echo

# Controlla Python
if ! command -v python3 &>/dev/null; then
    echo "[ERRORE] Python3 non trovato."
    echo "Installa con: brew install python (Mac) o sudo apt install python3 (Linux)"
    exit 1
fi
echo "[OK] Python3 trovato: $(python3 --version)"

# Dipendenze
echo
echo "Installazione dipendenze..."
pip3 install mido python-rtmidi pyautogui --quiet

# Linux: pyautogui richiede alcune librerie di sistema
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo
    echo "Linux rilevato - potrebbe servire:"
    echo "  sudo apt install python3-tk python3-xlib scrot"
fi

echo
echo "Avvio MIDI StreamDeck..."
python3 midi_streamdeck.py
