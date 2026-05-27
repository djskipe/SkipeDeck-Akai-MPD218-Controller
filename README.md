# 🎛️ SkipeDeck – Trasforma l’Akai MPD218 in uno Stream Deck

**SkipeDeck** è un’applicazione Python che trasforma il controller MIDI **Akai MPD218** in una centrale di controllo personalizzabile, simile a uno Stream Deck.  
Grazie a un’interfaccia grafica con foto interattiva, puoi assegnare ai 16 pad e ai 6 knob qualsiasi azione: scorciatoie da tastiera, apertura di programmi, comandi shell, controllo di Discord, Spotify e molto altro.

<img width="1235" height="736" alt="image" src="https://github.com/user-attachments/assets/9d4472c2-6d0e-4286-911d-9cc0f539d88f" />


---

## ✨ Funzionalità principali

- **Foto interattiva** – clicca sui pad nell’immagine per configurarli o eseguire azioni.
- **16 pad + 6 knob** completamente personalizzabili.
- **Mappatura MIDI (Learn Mode)** – associa facilmente i pad fisici alle aree della foto.
- **Azioni supportate**:
  - Shortcut tastiera (es. `Ctrl+Shift+M`)
  - Apri applicazione (`.exe`, percorso o nome)
  - Esegui comando shell
  - Discord: muto/unmuto / deafen/undeafen
  - Spotify: play/pausa, brano successivo/precedente
  - **Trimmer (knob)**: Volume sistema, seek video (← →), scorrimento pagine (↑ ↓)
- **Calibrazione integrata** – adatta i riquadri alla tua immagine (anche ad alta risoluzione).
- **Profili multipli** – salva configurazioni diverse e passaci da un menù a tendina.
- **Salvataggio automatico** – tutte le impostazioni vengono memorizzate in file JSON.
- **Feedback visivo** – il pad premuto lampeggia in rosso sulla foto.
- **Supporto immagini personalizzate** – sostituisci `mpd218.png` con la tua foto.

---

## 📦 Requisiti e installazione

**Sistema:** Windows (10/11) – può funzionare anche su Linux/Mac con le dovute dipendenze.  
**Python:** 3.8 o superiore.

### Avvio rapido (Windows)
1. Scarica o clona il repository.
2. Fai doppio clic su **`avvia.bat`**.
   - Installa automaticamente i pacchetti necessari (`pygame`, `pyautogui`, `pillow`).
   - Lancia l’applicazione.
3. Collega l’MPD218 via USB **prima** di avviare (o premi **🔄 Connetti** nell’app).

### Avvio manuale (qualsiasi OS)
```bash
pip install pygame pyautogui pillow
python midi_streamdeck.py
