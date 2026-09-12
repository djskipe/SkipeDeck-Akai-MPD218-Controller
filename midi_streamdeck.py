#!/usr/bin/env python3
"""
MIDI StreamDeck — Versione Definitiva: Foto Interattiva + Macro + Calibrazione + Profili
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, json, subprocess, os, sys, time
from pathlib import Path
from PIL import Image, ImageTk

# ── Dipendenze opzionali ───────────────────────────────────────────────────────
try:
    import pygame.midi as pmidi
    MIDI_OK = True
except ImportError:
    MIDI_OK = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    AUTO_OK = True
except ImportError:
    AUTO_OK = False

try:
    from pynput import keyboard as pynput_kb
    PYNPUT_OK = True
except ImportError:
    PYNPUT_OK = False

import ctypes as _ctypes, sys as _sys, time as _time_mod

_VK = {
    'ctrl':0x11,'control':0x11,'shift':0x10,'alt':0x12,'win':0x5B,
    'enter':0x0D,'return':0x0D,'space':0x20,'tab':0x09,
    'esc':0x1B,'escape':0x1B,'backspace':0x08,
    'delete':0x2E,'del':0x2E,'insert':0x2D,
    'home':0x24,'end':0x23,'pageup':0x21,'pagedown':0x22,
    'left':0x25,'up':0x26,'right':0x27,'down':0x28,
    'f1':0x70,'f2':0x71,'f3':0x72,'f4':0x73,'f5':0x74,'f6':0x75,
    'f7':0x76,'f8':0x77,'f9':0x78,'f10':0x79,'f11':0x7A,'f12':0x7B,
    'f13':0x7C,'f14':0x7D,'f15':0x7E,'f16':0x7F,
    'f17':0x80,'f18':0x81,'f19':0x82,'f20':0x83,
    'f21':0x84,'f22':0x85,'f23':0x86,'f24':0x87,
    'pause':0x13,'break':0x03,'cancel':0x03,
    'printscreen':0x2C,'scrolllock':0x91,'numlock':0x90,'capslock':0x14,
    'playpause':0xB3,'nexttrack':0xB0,'prevtrack':0xB1,
    'volumeup':0xAF,'volumedown':0xAE,'mute':0xAD,
    'media_stop':0xB2, 'browser_home':0xAC,
    'launch_mail':0xB4, 'launch_media':0xB5,
    'menu':0x5D,
}
for _c in 'abcdefghijklmnopqrstuvwxyz': _VK[_c] = ord(_c.upper())
for _d in '0123456789':                 _VK[_d] = ord(_d)

# Numpad
_VK['numpad0'] = 0x60
_VK['numpad1'] = 0x61
_VK['numpad2'] = 0x62
_VK['numpad3'] = 0x63
_VK['numpad4'] = 0x64
_VK['numpad5'] = 0x65
_VK['numpad6'] = 0x66
_VK['numpad7'] = 0x67
_VK['numpad8'] = 0x68
_VK['numpad9'] = 0x69
_VK['numpad/'] = 0x6F
_VK['numpad*'] = 0x6A
_VK['numpad-'] = 0x6D
_VK['numpad+'] = 0x6B
_VK['numpad.'] = 0x6E
_VK['numpadenter'] = 0x0D

# Simboli
_VK['/']  = 0xBF
_VK['\\'] = 0xDC
_VK[';']  = 0xBA
_VK["'"]  = 0xDE
_VK['[']  = 0xDB
_VK[']']  = 0xDD
_VK[',']  = 0xBC
_VK['.']  = 0xBE
_VK['-']  = 0xBD
_VK['=']  = 0xBB
_VK['`']  = 0xC0

def _press_hotkey(combo: str, repeats=1):
    keys = [k.strip().lower() for k in combo.split('+') if k.strip()]
    vks  = [_VK[k] for k in keys if k in _VK]
    if not vks: return
    if _sys.platform == 'win32':
        u32 = _ctypes.windll.user32
        for _ in range(repeats):
            for vk in vks: u32.keybd_event(vk, 0, 0, 0); _time_mod.sleep(0.001)
            _time_mod.sleep(0.01)
            for vk in reversed(vks): u32.keybd_event(vk, 0, 2, 0); _time_mod.sleep(0.001)
    elif AUTO_OK:
        for _ in range(repeats): pyautogui.hotkey(*keys)

def _press_media(key: str, repeats=1):
    vk = _VK.get(key)
    if vk and _sys.platform == 'win32':
        u32 = _ctypes.windll.user32
        for _ in range(repeats):
            u32.keybd_event(vk, 0, 0, 0); _time_mod.sleep(0.02); u32.keybd_event(vk, 0, 2, 0)
    elif AUTO_OK:
        for _ in range(repeats): pyautogui.press(key)

# ── Impostazioni Costanti ─────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
SAVE_FILE = BASE_DIR / "streamdeck_config.json"
PROFILES_FILE = BASE_DIR / "profiles.json"
MODEL_FILE = BASE_DIR / "model.txt"

DEFAULT_NOTES = {
    68: "p1",  69: "p2",  70: "p3",  71: "p4",
    72: "p5",  73: "p6",  74: "p7",  75: "p8",
    76: "p9",  77: "p10", 78: "p11", 79: "p12",
    80: "p13", 81: "p14", 82: "p15", 83: "p16"
}

KNOB_CCS = {}
KNOB_CCS_DEFAULT = {22: "k0", 23: "k1", 24: "k2", 25: "k3", 26: "k4", 27: "k5"}

DEFAULT_PAD_COORDS = {
    "p13": (191, 60, 257, 126), "p14": (270, 63, 336, 129),
    "p15": (359, 60, 425, 126), "p16": (447, 62, 513, 128),
    "p9":  (189,147, 255, 213), "p10": (275,145, 341, 211),
    "p11": (359,142, 425, 208), "p12": (445,143, 511, 209),
    "p5":  (186,225, 252, 291), "p6":  (274,222, 340, 288),
    "p7":  (361,222, 427, 288), "p8":  (448,222, 514, 288),
    "p1":  (189,305, 255, 371), "p2":  (274,306, 340, 372),
    "p3":  (360,304, 426, 370), "p4":  (449,305, 515, 371),
}

MODELS = {
    "inverted": {
        "name": "MPD218 Inverted (manopole 5-6 in basso)",
        "image": "mpd218_inverted.png",
        "crop": None,
        "knob_coords": {
            "k0": (30, 245, 60, 275),
            "k1": (111, 245, 141, 275),
            "k2": (27, 162, 57, 192),
            "k3": (111, 162, 141, 192),
            "k4": (32, 78, 63, 112),
            "k5": (114, 82, 144, 112),
        },
    },
    "standard": {
        "name": "MPD218 Standard (manopole 5-6 in alto)",
        "image": "mpd218_standard.png",
        "crop": None,
        "knob_coords": {
            "k4": (80, 94, 110, 128),
            "k5": (145, 96, 175, 126),
            "k2": (83, 171, 113, 201),
            "k3": (145, 173, 175, 203),
            "k0": (81, 248, 111, 278),
            "k1": (144, 245, 174, 275),
        },
    },
}

ACTION_TYPES = [
    "— nessuna —", "Shortcut tastiera", "Apri applicazione", "Esegui comando",
    "Discord: muto/unmuto", "Discord: deafen/undeafen", "Spotify: play/pausa",
    "Spotify: prossimo", "Spotify: precedente", "Trimmer: Volume OS (Su/Giù)",
    "Trimmer: Player Video YouTube/VLC", "Trimmer: Scorrimento Pagine"
]
COLORS = {
    "— nessuna —": "#2e2e2e", "Shortcut tastiera": "#3498db", "Apri applicazione": "#2ecc71",
    "Esegui comando": "#f1c40f", "Discord: muto/unmuto": "#9b59b6", "Discord: deafen/undeafen":"#9b59b6",
    "Spotify: play/pausa": "#1db954", "Spotify: prossimo": "#1db954", "Spotify: precedente": "#1db954",
    "Trimmer: Volume OS (Su/Giù)": "#e67e22", "Trimmer: Player Video YouTube/VLC": "#e67e22",
    "Trimmer: Scorrimento Pagine": "#e67e22"
}


# ══════════════════════════════════════════════════════════════════════════════
def load_model_image(model_data):
    img = Image.open(BASE_DIR / model_data["image"])
    if model_data.get("crop"):
        img = img.crop(model_data["crop"])
    img = img.resize((550, 450))
    return img


def load_coords_for_model(model_name):
    pad_file = BASE_DIR / f"pad_coordinates_{model_name}.json"
    knob_file = BASE_DIR / f"knob_coordinates_{model_name}.json"
    
    pads = dict(DEFAULT_PAD_COORDS)
    if pad_file.exists():
        try:
            data = json.loads(pad_file.read_text())
            pads = {k: tuple(v) for k, v in data.items()}
        except: pass
    
    knobs = dict(MODELS[model_name]["knob_coords"])
    if knob_file.exists():
        try:
            data = json.loads(knob_file.read_text())
            knobs = {k: tuple(v) for k, v in data.items()}
        except: pass
    
    return pads, knobs


# ══════════════════════════════════════════════════════════════════════════════
class ModelChooser(tk.Toplevel):
    def __init__(self, parent, current="inverted"):
        super().__init__(parent)
        self.title("Seleziona il tuo MPD218")
        self.configure(bg="#1c1c24")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.result = current

        tk.Label(self, text="Quale modello di MPD218 hai?",
                 fg="white", bg="#1c1c24", font=("",14,"bold")).pack(pady=(15,5))
        tk.Label(self, text="Scegli la versione con la disposizione delle manopole corretta.",
                 fg="#aaa", bg="#1c1c24", font=("",9)).pack(pady=(0,15))

        frame = tk.Frame(self, bg="#1c1c24")
        frame.pack(padx=20, pady=10)

        self._choice_var = tk.StringVar(value=current)
        self._imgs = {}

        for idx, (key, data) in enumerate(MODELS.items()):
            card = tk.Frame(frame, bg="#2a2a36", bd=2, relief="solid", padx=10, pady=10)
            card.grid(row=0, column=idx, padx=10)

            try:
                img = load_model_image(data).resize((200, 160))
                photo = ImageTk.PhotoImage(img)
                self._imgs[key] = photo
                tk.Label(card, image=photo, bg="#2a2a36").pack()
            except Exception:
                tk.Label(card, text="(immagine non trovata)", bg="#2a2a36", fg="#888",
                         width=25, height=8).pack()

            tk.Radiobutton(card, text=data["name"], variable=self._choice_var,
                           value=key, bg="#2a2a36", fg="white", selectcolor="#1c1c24",
                           activebackground="#2a2a36", activeforeground="white",
                           font=("",9,"bold"), wraplength=180, justify="center").pack(pady=5)

        tk.Button(self, text="✅ Conferma", command=self._ok,
                  bg="#2a6eba", fg="white", bd=0, padx=20, pady=8,
                  font=("",10,"bold")).pack(pady=15)

        self.geometry(f"+{parent.winfo_x()+200}+{parent.winfo_y()+100}")

    def _ok(self):
        self.result = self._choice_var.get()
        self.destroy()

    @classmethod
    def ask(cls, parent, current="inverted"):
        d = cls(parent, current)
        parent.wait_window(d)
        return d.result


# ══════════════════════════════════════════════════════════════════════════════
class KeyRecorder(tk.Toplevel):
    """Registratore di scorciatoie usando 'pynput' (cattura TUTTI i tasti)."""
    def __init__(self, parent, current=""):
        super().__init__(parent)
        self.title("Registra Scorciatoia")
        self.configure(bg="#1c1c24")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.result = None
        self.keys = []
        self._recording = True
        self._listener = None

        tk.Label(self, text="Premi la combinazione di tasti desiderata...",
                 fg="white", bg="#1c1c24", font=("",11), pady=8).pack()
        
        self._lbl = tk.Label(self, text="In attesa...", fg="#666", bg="#0a0a0a",
                              font=("Consolas",14,"bold"), padx=20, pady=15, width=30)
        self._lbl.pack(padx=10, pady=5)
        
        self._hint = tk.Label(self, text="ESC per annullare · INVIO per confermare",
                               fg="#888", bg="#1c1c24", font=("",8))
        self._hint.pack()

        f = tk.Frame(self, bg="#1c1c24")
        f.pack(fill="x", padx=10, pady=10)
        tk.Button(f, text="Cancella", command=self._clear, bg="#444", fg="white", bd=0, padx=10, pady=4).pack(side="left")
        tk.Button(f, text="✅ OK", command=self._ok, bg="#2a6eba", fg="white", bd=0, padx=20, pady=4, font=("",9,"bold")).pack(side="right")

        self.geometry(f"+{parent.winfo_x()+150}+{parent.winfo_y()+150}")

        if PYNPUT_OK:
            self.after(150, self._start_listener)
        else:
            self._lbl.config(text="Libreria 'pynput' non installata!", fg="#e74c3c")
            self._hint.config(text="Esegui: pip install pynput")

    def _start_listener(self):
        from pynput import keyboard as pk

        def on_press(key):
            if not self._recording:
                return False
            
            try:
                # ── PRIMA controlla il codice VK per distinguere numpad ──
                vk = getattr(key, 'vk', None)
                if vk is not None:
                    # Numpad numeri (0x60 - 0x69)
                    if 0x60 <= vk <= 0x69:
                        numpad_num = vk - 0x60
                        self._add_key(f'numpad{numpad_num}')
                        return
                    # Numpad operatori
                    elif vk == 0x6F:
                        self._add_key('numpad/'); return
                    elif vk == 0x6A:
                        self._add_key('numpad*'); return
                    elif vk == 0x6D:
                        self._add_key('numpad-'); return
                    elif vk == 0x6B:
                        self._add_key('numpad+'); return
                    elif vk == 0x6E:
                        self._add_key('numpad.'); return
                
                # ── Modificatori ──
                if key in (pk.Key.ctrl_l, pk.Key.ctrl_r, pk.Key.ctrl):
                    self._add_key('ctrl')
                elif key in (pk.Key.shift_l, pk.Key.shift_r, pk.Key.shift):
                    self._add_key('shift')
                elif key in (pk.Key.alt_l, pk.Key.alt_r, pk.Key.alt, pk.Key.alt_gr):
                    self._add_key('alt')
                elif key in (pk.Key.cmd, pk.Key.cmd_l, pk.Key.cmd_r):
                    self._add_key('win')
                
                # ── Tasti di controllo ──
                elif key == pk.Key.esc:
                    self.after(0, self._cancel)
                    return False
                elif key == pk.Key.enter:
                    self.after(0, self._ok)
                    return False
                elif key == pk.Key.space:
                    self._add_key('space')
                elif key == pk.Key.tab:
                    self._add_key('tab')
                elif key == pk.Key.backspace:
                    self._add_key('backspace')
                elif key == pk.Key.delete:
                    self._add_key('delete')
                elif key == pk.Key.insert:
                    self._add_key('insert')
                elif key == pk.Key.home:
                    self._add_key('home')
                elif key == pk.Key.end:
                    self._add_key('end')
                elif key == pk.Key.page_up:
                    self._add_key('pageup')
                elif key == pk.Key.page_down:
                    self._add_key('pagedown')
                elif key == pk.Key.up:
                    self._add_key('up')
                elif key == pk.Key.down:
                    self._add_key('down')
                elif key == pk.Key.left:
                    self._add_key('left')
                elif key == pk.Key.right:
                    self._add_key('right')
                elif key == pk.Key.caps_lock:
                    self._add_key('capslock')
                elif key == pk.Key.num_lock:
                    self._add_key('numlock')
                elif key == pk.Key.scroll_lock:
                    self._add_key('scrolllock')
                elif key == pk.Key.print_screen:
                    self._add_key('printscreen')
                elif key == pk.Key.pause:
                    self._add_key('pause')
                elif key == pk.Key.menu:
                    self._add_key('menu')
                
                # ── Tasti funzione F1-F24 ──
                elif hasattr(pk.Key, 'f1'):
                    matched = False
                    for i in range(1, 25):
                        fkey = getattr(pk.Key, f'f{i}', None)
                        if fkey is not None and key == fkey:
                            self._add_key(f'f{i}')
                            matched = True
                            break
                    if not matched and hasattr(key, 'char') and key.char:
                        self._add_key(key.char.lower())
                
                # ── Caratteri normali ──
                elif hasattr(key, 'char') and key.char:
                    self._add_key(key.char.lower())
            
            except Exception as e:
                print(f"KeyRecorder error: {e}")

        def on_release(key):
            if not self._recording:
                return False

        self._listener = pk.Listener(on_press=on_press, on_release=on_release)
        self._listener.daemon = True
        self._listener.start()

    def _add_key(self, name):
        if not name:
            return
        if name in self.keys:
            return
        if name in ('ctrl', 'shift', 'alt', 'win'):
            self.keys.insert(0, name)
        else:
            self.keys.append(name)
        self.after(0, self._update_display)

    def _update_display(self):
        if self.keys:
            self._lbl.config(text=" + ".join(k.upper() for k in self.keys), fg="#58d68d")
        else:
            self._lbl.config(text="In attesa...", fg="#666")

    def _clear(self):
        self.keys = []
        self._update_display()

    def _ok(self):
        if not self.keys:
            return
        self._recording = False
        self.result = "+".join(self.keys)
        self._close()

    def _cancel(self):
        self._recording = False
        self.result = None
        self._close()

    def _close(self):
        try:
            if self._listener is not None:
                self._listener.stop()
        except:
            pass
        self.destroy()

    @classmethod
    def ask(cls, parent, current=""):
        d = cls(parent, current)
        parent.wait_window(d)
        return d.result
        
# ══════════════════════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SkipeDeck - Akai MPD218 Controller")
        self.root.geometry("1100x620")
        self.root.configure(bg="#111")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.cfg = {}
        self.note_map = dict(DEFAULT_NOTES)
        self.selected = None
        self.learn = False
        self.running = False
        self.midi_thread = None
        self.last_trig = {}
        self.knob_vals = {}
        self.knob_btns = {}
        self.active_leds = {}
        self.active_knob_leds = {}
        
        self.current_profile = "inverted"
        self.profiles = {
            "inverted": {
                "note_map": {str(k): v for k, v in DEFAULT_NOTES.items()},
                "cfg": {},
                "knob_cc_map": {str(cc): k for cc, k in KNOB_CCS_DEFAULT.items()}
            }
        }
        self.profile_assignments = {}
        
        self.calibrate_mode = False
        self.cal_drag_pad = None
        self.cal_drag_start = None
        self.cal_drag_element_type = None
        self.cal_rect_ids = {}
        self.pad_handles = {}
        self.knob_handles = {}
        self._knob_timer_ids = {}
        
        self.current_model = "inverted"
        if MODEL_FILE.exists():
            saved = MODEL_FILE.read_text().strip()
            if saved in MODELS:
                self.current_model = saved
        else:
            chosen = ModelChooser.ask(self.root, self.current_model)
            if chosen in MODELS:
                self.current_model = chosen
            MODEL_FILE.write_text(self.current_model)
        
        self.coordinates, self.knob_coordinates = load_coords_for_model(self.current_model)

        self._load_profiles()
        self._load_knob_cc_map()
        self._ui()
        self._start_midi()

    def _on_closing(self):
        self.running = False
        if self.midi_thread and self.midi_thread.is_alive():
            self.midi_thread.join(timeout=0.2)
        self._save_profiles()
        self.root.destroy()

    def _load_profiles(self):
        global PROFILES_FILE
        if PROFILES_FILE.exists():
            try:
                data = json.loads(PROFILES_FILE.read_text())
                self.profiles = data.get("profiles", {"inverted": {"note_map": {str(k): v for k, v in DEFAULT_NOTES.items()}, "cfg": {}, "knob_cc_map": {str(cc): k for cc, k in KNOB_CCS_DEFAULT.items()}}})
                self.profile_assignments = data.get("assignments", {})
                self.current_profile = data.get("current", "inverted")
                if self.current_profile in self.profiles:
                    profile_data = self.profiles[self.current_profile]
                    note_map_raw = profile_data.get("note_map", {})
                    self.note_map = {int(k): v for k, v in note_map_raw.items()} if note_map_raw else dict(DEFAULT_NOTES)
                    self.cfg = profile_data.get("cfg", {})
            except Exception as e:
                self._log(f"Errore caricamento profili: {e}")
                self.profiles = {"inverted": {"note_map": {str(k): v for k, v in DEFAULT_NOTES.items()}, "cfg": {}, "knob_cc_map": {str(cc): k for cc, k in KNOB_CCS_DEFAULT.items()}}}
                self.current_profile = "inverted"

    def _load_knob_cc_map(self):
        global KNOB_CCS
        KNOB_CCS.clear()
        knob_map = self.profiles.get(self.current_profile, {}).get("knob_cc_map", {})
        if knob_map:
            for cc_str, k_id in knob_map.items():
                KNOB_CCS[int(cc_str)] = k_id
        else:
            KNOB_CCS.update(KNOB_CCS_DEFAULT)

    def _save_knob_cc_map(self):
        if self.current_profile not in self.profiles:
            self.profiles[self.current_profile] = {}
        self.profiles[self.current_profile]["knob_cc_map"] = {
            str(cc): k_id for cc, k_id in KNOB_CCS.items()
        }

    def _save_profiles(self):
        global PROFILES_FILE
        self.profiles[self.current_profile] = {
            "note_map": {str(k): v for k, v in self.note_map.items()},
            "cfg": dict(self.cfg)
        }
        self._save_knob_cc_map()
        data = {
            "profiles": self.profiles,
            "assignments": self.profile_assignments,
            "current": self.current_profile
        }
        PROFILES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def _switch_profile(self, profile_name):
        if profile_name not in self.profiles:
            return
        self.profiles[self.current_profile] = {
            "note_map": {str(k): v for k, v in self.note_map.items()},
            "cfg": dict(self.cfg)
        }
        self._save_knob_cc_map()
        self.current_profile = profile_name
        profile_data = self.profiles[profile_name]
        note_map_raw = profile_data.get("note_map", {})
        self.note_map = {int(k): v for k, v in note_map_raw.items()} if note_map_raw else dict(DEFAULT_NOTES)
        self.cfg = profile_data.get("cfg", {})
        self._load_knob_cc_map()
        self._log(f"🔄 Profilo cambiato: {profile_name}")
        self._update_profile_indicator()
        self._refresh_profile_combo()
        self._refresh_all_assignments()
        self._save_profiles()

    def _update_profile_indicator(self):
        if hasattr(self, '_profile_lbl'):
            self._profile_lbl.config(text=f"Profilo: {self.current_profile}")

    def _cancel_new_profile(self):
        self._new_profile_var.set("")
        self._new_profile_frame.pack_forget()

    def _create_profile(self):
        if not self._new_profile_frame.winfo_ismapped():
            self._new_profile_var.set("")
            self._new_profile_frame.pack(fill="x", pady=3, after=self._profile_combo.master)
            self._new_profile_entry.focus()
            return
        name = self._new_profile_var.get().strip()
        if not name:
            messagebox.showwarning("Attenzione", "Inserisci un nome per il profilo!")
            return
        if name in self.profiles:
            messagebox.showwarning("Attenzione", f"Il profilo '{name}' esiste già!")
            return
        self.profiles[name] = {
            "note_map": {str(k): v for k, v in DEFAULT_NOTES.items()},
            "cfg": {},
            "knob_cc_map": {str(cc): k for cc, k in KNOB_CCS_DEFAULT.items()}
        }
        self._new_profile_var.set("")
        self._new_profile_frame.pack_forget()
        self._refresh_profile_combo()
        self._save_profiles()
        self._log(f"✅ Profilo '{name}' creato")
        self._switch_profile(name)

    def _delete_profile(self):
        name = self._profile_combo_var.get()
        if name in ("inverted", "Default"):
            messagebox.showwarning("Attenzione", f"Non puoi eliminare il profilo '{name}'!")
            return
        if len(self.profiles) <= 1:
            messagebox.showwarning("Attenzione", "Deve esserci almeno un profilo!")
            return
        if messagebox.askyesno("Conferma", f"Eliminare il profilo '{name}'?\n\nTutte le configurazioni andranno perse!"):
            if name == self.current_profile:
                self._switch_profile("inverted")
            del self.profiles[name]
            self._refresh_profile_combo()
            self._save_profiles()
            self._log(f"🗑 Profilo '{name}' eliminato")

    def _browse_profile_path(self):
        path = filedialog.askdirectory(
            initialdir=self._profile_path_var.get(),
            title="Scegli la cartella per salvare i profili"
        )
        if path:
            self._profile_path_var.set(path)
            global PROFILES_FILE
            PROFILES_FILE = Path(path) / "profiles.json"
            self._log(f"📁 Profili salvati in: {path}")
            self._save_profiles()

    def _show_unused_buttons_info(self):
        info_text = "⚠️ PULSANTI NON UTILIZZABILI:\n\n"
        info_text += "• CTRL BANK, PAD BANK, FULL LEVEL\n"
        info_text += "• PROG SELECT, NR CONFIG, NOTE REPEAT\n\n"
        info_text += "Questi pulsanti non inviano segnali MIDI utilizzabili\n"
        info_text += "o modificano il comportamento interno dell'MPD218.\n"
        info_text += "Pertanto sono stati rimossi dall'interfaccia."
        messagebox.showinfo("Pulsanti non supportati", info_text)

    def _on_model_change(self, event=None):
        selected_name = self._model_var.get()
        for key, data in MODELS.items():
            if data["name"] == selected_name:
                self.current_model = key
                break
        MODEL_FILE.write_text(self.current_model)
        
        if self.current_model in self.profiles and self.current_model != self.current_profile:
            self._switch_profile(self.current_model)
            self._refresh_profile_combo()
        
        self.coordinates, self.knob_coordinates = load_coords_for_model(self.current_model)
        
        try:
            model_data = MODELS[self.current_model]
            img = load_model_image(model_data)
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        except Exception as e:
            self._log(f"Errore caricamento immagine: {e}")
        
        self._refresh_all_assignments()
        self._log(f"🔄 Modello cambiato: {MODELS[self.current_model]['name']} → profilo: {self.current_profile}")

    def _ui(self):
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        sb = tk.Frame(self.root, bg="#1a1a2e", pady=4)
        sb.grid(row=0, column=0, sticky="ew")
        self._dot = tk.Label(sb, text="●", fg="#e74c3c", bg="#1a1a2e", font=("",12))
        self._dot.pack(side="left", padx=6)
        self._slbl = tk.Label(sb, text="Disconnesso", fg="#aaa", bg="#1a1a2e", font=("Helvetica",9))
        self._slbl.pack(side="left")
        self._cal_ind = tk.Label(sb, text="", fg="#ff9800", bg="#1a1a2e", font=("Helvetica",9,"bold"))
        self._cal_ind.pack(side="left", padx=10)
        self._profile_lbl = tk.Label(sb, text=f"Profilo: {self.current_profile}", fg="#4a90d9", bg="#1a1a2e", font=("Helvetica",9,"bold"))
        self._profile_lbl.pack(side="left", padx=15)
        
        self._model_var = tk.StringVar(value=MODELS[self.current_model]["name"])
        model_combo = ttk.Combobox(sb, textvariable=self._model_var,
                                    values=[m["name"] for m in MODELS.values()],
                                    state="readonly", width=38)
        model_combo.pack(side="right", padx=6)
        model_combo.bind("<<ComboboxSelected>>", self._on_model_change)
        tk.Label(sb, text="Modello:", fg="#888", bg="#1a1a2e", font=("",8)).pack(side="right")
        
        self._dev = tk.StringVar()
        self._dcb = ttk.Combobox(sb, textvariable=self._dev, state="readonly", width=22)
        self._dcb.pack(side="right", padx=6)
        tk.Button(sb, text="🔄 Connetti", command=self._start_midi, bg="#333", fg="white", bd=0, padx=8, pady=2).pack(side="right")

        body = tk.Frame(self.root, bg="#111")
        body.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.columnconfigure(2, weight=2)

        k_frame = tk.Frame(body, bg="#141419", bd=1, relief="solid", padx=10, pady=10)
        k_frame.grid(row=0, column=0, sticky="nsew", padx=(0,4))
        for r in range(3):
            k_frame.rowconfigure(r, weight=1)
        for c in range(2):
            k_frame.columnconfigure(c, weight=1)

        knob_layout = [
            ("k0", 0, 0), ("k1", 0, 1),
            ("k2", 1, 0), ("k3", 1, 1),
            ("k4", 2, 0), ("k5", 2, 1)
        ]
        for idx, (k_id, row, col) in enumerate(knob_layout):
            b = tk.Button(k_frame, text=f"MANOPOLA {idx+1}\n[Inattiva]", bg="#222", fg="#888",
                          font=("Helvetica",8), bd=2, relief="groove", command=lambda k=k_id, n=f"Manopola {idx+1}": self._sel(k, n))
            b.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
            self.knob_btns[k_id] = b

        disclaimer = tk.Label(k_frame, text="⚠️ I tasti CTRL BANK, PAD BANK,\nFULL LEVEL, PROG SELECT, NR CONFIG,\nNOTE REPEAT non inviano segnali MIDI.\nNon sono utilizzabili.",
                              bg="#141419", fg="#ffaa00", font=("Helvetica",7), justify="left")
        disclaimer.grid(row=3, column=0, columnspan=2, pady=(10,0), sticky="w")

        c_frame = tk.Frame(body, bg="#111")
        c_frame.grid(row=0, column=1, sticky="nsew", padx=(0,4))
        self.canvas = tk.Canvas(c_frame, width=550, height=450, bg="#111", highlightthickness=0)
        self.canvas.pack(expand=True)
        try:
            model_data = MODELS[self.current_model]
            img = load_model_image(model_data)
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        except Exception as e:
            self.canvas.create_text(275, 225, text=f"Errore immagine:\n{e}", fill="white")
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        right = tk.Frame(body, bg="#1a1a26", padx=12, pady=12, bd=1, relief="solid")
        right.grid(row=0, column=2, sticky="nsew")

        tk.Label(right, text="CONFIGURATORE SELEZIONE", font=("Helvetica",11,"bold"), fg="white", bg="#1a1a26").pack(anchor="w")
        self._sel_lbl = tk.Label(right, text="← Clicca sulla foto, su una manopola o toccalo sull'Akai", fg="#888", bg="#1a1a26")
        self._sel_lbl.pack(anchor="w", pady=(2,10))

        self._name = tk.StringVar()
        f_lbl = tk.Frame(right, bg="#1a1a26")
        f_lbl.pack(fill="x", pady=3)
        tk.Label(f_lbl, text="Etichetta:", fg="#bbb", bg="#1a1a26", width=10, anchor="w").pack(side="left")
        tk.Entry(f_lbl, textvariable=self._name, bg="#0d1117", fg="white", insertbackground="white", relief="flat").pack(side="left", fill="x", expand=True)

        self._action = tk.StringVar(value="— nessuna —")
        f_act = tk.Frame(right, bg="#1a1a26")
        f_act.pack(fill="x", pady=4)
        tk.Label(f_act, text="Azione:", fg="#bbb", bg="#1a1a26", width=10, anchor="w").pack(side="left")
        cb = ttk.Combobox(f_act, textvariable=self._action, values=ACTION_TYPES, state="readonly")
        cb.pack(side="left", fill="x", expand=True)
        cb.bind("<<ComboboxSelected>>", self._on_action)

        self._val = tk.StringVar()
        self._val_lbl = tk.Label(right, text="Parametro / Comando / Tasti:", fg="#bbb", bg="#1a1a26", anchor="w")
        self._val_lbl.pack(anchor="w", pady=(4,0))
        val_f = tk.Frame(right, bg="#1a1a26")
        val_f.pack(fill="x", pady=2)
        self._val_entry = tk.Entry(val_f, textvariable=self._val, bg="#0d1117", fg="white", insertbackground="white", relief="flat")
        self._val_entry.pack(side="left", fill="x", expand=True)
        self._browse_btn = tk.Button(val_f, text="📁", command=self._browse, bg="#333", fg="white", bd=0, padx=6)
        self._record_btn = tk.Button(val_f, text="⌨ Registra", command=self._record_shortcut, bg="#1a3a6a", fg="white", bd=0, padx=8)

        self._help = tk.Label(right, text="", fg="#aaa", bg="#1a1a26", font=("",8), wraplength=280, justify="left")
        self._help.pack(anchor="w", pady=5)

        btn_f = tk.Frame(right, bg="#1a1a26")
        btn_f.pack(anchor="w", pady=6)
        self._ok_btn = tk.Button(btn_f, text="✅ Applica", command=self._apply, bg="#2a6eba", fg="white", bd=0, padx=12, pady=5, font=("",9,"bold"), state="disabled")
        self._ok_btn.pack(side="left", padx=(0,6))
        self._del_btn = tk.Button(btn_f, text="🗑 Rimuovi", command=self._remove, bg="#c0392b", fg="white", bd=0, padx=10, pady=5, state="disabled")
        self._del_btn.pack(side="left")
        self._learn_btn = tk.Button(right, text="🎯 Mappatura MIDI (Learn)", command=self._toggle_learn, bg="#e67e22", fg="white", bd=0, padx=10, pady=4, state="disabled")
        self._learn_btn.pack(anchor="w", pady=6)

        profile_frame = tk.LabelFrame(right, text="🎭 PROFILI", fg="#ff9800", bg="#1a1a26", font=("",10,"bold"))
        profile_frame.pack(fill="x", pady=(15,5))

        tk.Label(profile_frame, text="📌 Profilo attuale:", fg="#aaa", bg="#1a1a26", font=("",8)).pack(anchor="w", pady=(5,2))
        current_frame = tk.Frame(profile_frame, bg="#1a1a26")
        current_frame.pack(fill="x", pady=2)
        self._profile_combo_var = tk.StringVar(value=self.current_profile)
        self._profile_combo = ttk.Combobox(current_frame, textvariable=self._profile_combo_var, state="readonly", width=16, font=("",10))
        self._profile_combo.pack(side="left", fill="x", expand=True)
        self._profile_combo.bind("<<ComboboxSelected>>", self._on_profile_combo_select)
        tk.Button(current_frame, text="➕ Nuovo", command=self._create_profile, bg="#27ae60", fg="white", bd=0, padx=6, pady=2, font=("",8)).pack(side="left", padx=2)
        tk.Button(current_frame, text="🗑 Elimina", command=self._delete_profile, bg="#c0392b", fg="white", bd=0, padx=6, pady=2, font=("",8)).pack(side="left")

        self._new_profile_frame = tk.Frame(profile_frame, bg="#1a1a26")
        tk.Label(self._new_profile_frame, text="Nome:", fg="#aaa", bg="#1a1a26", font=("",8)).pack(side="left", padx=2)
        self._new_profile_var = tk.StringVar()
        self._new_profile_entry = tk.Entry(self._new_profile_frame, textvariable=self._new_profile_var, width=12, bg="#0d1117", fg="white", font=("",9))
        self._new_profile_entry.pack(side="left", padx=2)
        tk.Button(self._new_profile_frame, text="✅", command=self._create_profile, bg="#27ae60", fg="white", bd=0, padx=4, pady=2, font=("",8)).pack(side="left", padx=1)
        tk.Button(self._new_profile_frame, text="❌", command=self._cancel_new_profile, bg="#666", fg="white", bd=0, padx=4, pady=2, font=("",8)).pack(side="left")

        tk.Label(profile_frame, text="💾 Salva in:", fg="#aaa", bg="#1a1a26", font=("",8)).pack(anchor="w", pady=(8,2))
        path_frame = tk.Frame(profile_frame, bg="#1a1a26")
        path_frame.pack(fill="x", pady=2)
        self._profile_path_var = tk.StringVar(value=str(BASE_DIR))
        self._profile_path_entry = tk.Entry(path_frame, textvariable=self._profile_path_var, bg="#0d1117", fg="#aaa", font=("",7), state="readonly")
        self._profile_path_entry.pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="📁 Sfoglia", command=self._browse_profile_path, bg="#444", fg="white", bd=0, padx=6, pady=2, font=("",7)).pack(side="left", padx=2)

        tk.Button(profile_frame, text="ℹ️ Perché non ci sono CTRL BANK ecc.?", command=self._show_unused_buttons_info,
                  bg="#333", fg="#888", bd=0, padx=4, pady=1, font=("",7)).pack(anchor="w", pady=(5,2))

        self._refresh_profile_combo()

        btn2 = tk.Frame(right, bg="#1a1a26")
        btn2.pack(anchor="w", side="bottom", pady=4)
        tk.Button(btn2, text="💾 Salva", command=self._save_profiles, bg="#27ae60", fg="white", bd=0, padx=8, pady=4).pack(side="left", padx=(0,4))
        tk.Button(btn2, text="📂 Importa", command=self._import, bg="#444", fg="white", bd=0, padx=8, pady=4).pack(side="left", padx=(0,4))
        tk.Button(btn2, text="⬆ Esporta", command=self._export, bg="#444", fg="white", bd=0, padx=8, pady=4).pack(side="left")
        tk.Button(btn2, text="🔧 Calibra", command=self._toggle_calibrate, bg="#ff6b35", fg="white", bd=0, padx=8, pady=4).pack(side="left", padx=(4,0))

        lf = tk.Frame(self.root, bg="#111", padx=8, pady=4)
        lf.grid(row=2, column=0, sticky="ew")
        self._log_w = tk.Text(lf, height=3, bg="#050505", fg="#58d68d", font=("Courier",8), state="disabled", relief="flat")
        self._log_w.pack(fill="x")

        self._refresh_all_assignments()
        self._update_profile_indicator()

    def _refresh_all_assignments(self):
        for key in list(self.coordinates.keys()):
            self._refresh_btn(key)
        for key in list(self.knob_coordinates.keys()):
            self._refresh_btn(key)
        self._draw_knob_assignments()

    def _draw_knob_assignments(self):
        self.canvas.delete("knob_assign")
        if self.calibrate_mode:
            return
        for k_id, (x1, y1, x2, y2) in self.knob_coordinates.items():
            cfg = self.cfg.get(k_id, {})
            action = cfg.get("action", "— nessuna —")
            if action != "— nessuna —":
                color = COLORS.get(action, "#aaa")
                cx = (x1+x2)/2
                cy = (y1+y2)/2
                r = (x2-x1)/2
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=2, tags="knob_assign")
                self.canvas.create_text(cx, cy, text=k_id.upper(), fill=color, font=("",7,"bold"), tags="knob_assign")
            if k_id == self.selected:
                cx = (x1+x2)/2
                cy = (y1+y2)/2
                r = (x2-x1)/2
                self.canvas.create_oval(cx-r-3, cy-r-3, cx+r+3, cy+r+3, outline="#00ffff", width=2, dash=(4,4), tags="knob_assign")

    def _refresh_btn(self, key):
        cfg = self.cfg.get(key, {})
        action = cfg.get("action", "— nessuna —")
        label = cfg.get("label", "")
        if key.startswith("p"):
            self.canvas.delete(f"assign_{key}")
            self.canvas.delete(f"sel_{key}")
            if key in self.coordinates:
                x1, y1, x2, y2 = self.coordinates[key]
                if action != "— nessuna —":
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                        outline=COLORS.get(action, "#aaa"), width=2,
                        tags=f"assign_{key}")
                if key == self.selected:
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                        outline="#00ffff", width=3, dash=(4,4),
                        tags=f"sel_{key}")
        else:
            btn = self.knob_btns.get(key)
            if btn:
                idx = int(key[1:]) + 1
                if action != "— nessuna —":
                    btn.config(bg=COLORS.get(action, "#222"), fg="white",
                               text=f"MANOPOLA {idx}\n{label}")
                else:
                    btn.config(bg="#222", fg="#666",
                               text=f"MANOPOLA {idx}\n[Inattiva]")
            self._draw_knob_assignments()

    def _toggle_calibrate(self):
        self.calibrate_mode = not self.calibrate_mode
        self.cal_drag_pad = None
        self.cal_drag_element_type = None
        if self.calibrate_mode:
            self._cal_ind.config(text="🔧 CALIBRAZIONE ATTIVA")
            self._draw_calibration_rects()
        else:
            self._cal_ind.config(text="")
            self._clear_calibration_rects()
            self._save_coordinates()
            self._refresh_all_assignments()
            self._log("Calibrazione terminata, coordinate salvate.")

    def _draw_calibration_rects(self):
        self._clear_calibration_rects()
        for pad_id, (x1, y1, x2, y2) in self.coordinates.items():
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00ff00", width=2, tags=("calibration", f"pad_{pad_id}", "move"))
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=pad_id.upper(), fill="#00ff00", font=("",8,"bold"), tags=("calibration",))
            handles = []
            for hx, hy, mode in [(x1, y1, 'nw'), (x2, y1, 'ne'), (x1, y2, 'sw'), (x2, y2, 'se')]:
                h = self.canvas.create_oval(hx-6, hy-6, hx+6, hy+6, fill="#ff8800", outline="#ffaa00", tags=("calibration", f"pad_{pad_id}", f"resize_{mode}"))
                handles.append(h)
            self.cal_rect_ids[pad_id] = rect
            self.pad_handles[pad_id] = handles
        for knob_id, (x1, y1, x2, y2) in self.knob_coordinates.items():
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#ffff00", width=2, tags=("calibration", f"knob_{knob_id}", "move"))
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=knob_id.upper(), fill="#ffff00", font=("",8,"bold"), tags=("calibration",))
            handles = []
            for hx, hy, mode in [(x1, y1, 'nw'), (x2, y1, 'ne'), (x1, y2, 'sw'), (x2, y2, 'se')]:
                h = self.canvas.create_oval(hx-5, hy-5, hx+5, hy+5, fill="#ffaa00", outline="#ffcc00", tags=("calibration", f"knob_{knob_id}", f"resize_{mode}"))
                handles.append(h)
            self.cal_rect_ids[knob_id] = rect
            self.knob_handles[knob_id] = handles

    def _clear_calibration_rects(self):
        self.canvas.delete("calibration")
        self.cal_rect_ids = {}
        self.pad_handles = {}
        self.knob_handles = {}

    def _save_coordinates(self):
        pad_file = BASE_DIR / f"pad_coordinates_{self.current_model}.json"
        knob_file = BASE_DIR / f"knob_coordinates_{self.current_model}.json"
        pad_file.write_text(json.dumps({k: list(v) for k, v in self.coordinates.items()}, indent=2))
        knob_file.write_text(json.dumps({k: list(v) for k, v in self.knob_coordinates.items()}, indent=2))
        self._log(f"Coordinate salvate per modello: {self.current_model}")

    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        if not self.calibrate_mode:
            for p_id, (x1, y1, x2, y2) in self.coordinates.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self._sel(p_id, f"PAD {p_id[1:]}")
                    self._flash_pad_on(p_id)
                    self.root.after(250, lambda k=p_id: self._flash_pad_off(k))
                    if p_id in self.cfg:
                        threading.Thread(target=self._exec_pad, args=(p_id,), daemon=True).start()
                    return
            for k_id, (x1, y1, x2, y2) in self.knob_coordinates.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self._sel(k_id, f"Knob {k_id.upper()}")
                    self._flash_knob_on(k_id, "CLICK")
                    self.root.after(400, lambda k=k_id: self._flash_knob_off(k))
                    if k_id in self.cfg:
                        cfg = self.cfg.get(k_id, {})
                        if cfg.get("action", "— nessuna —") not in ["— nessuna —"] and not cfg.get("action", "").startswith("Trimmer:"):
                            threading.Thread(target=self._exec_knob_click, args=(k_id,), daemon=True).start()
                    return
            return
        element_id = None
        element_type = None
        for pad_id, (x1, y1, x2, y2) in self.coordinates.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                element_id = pad_id
                element_type = 'pad'
                break
        if not element_id:
            for knob_id, (x1, y1, x2, y2) in self.knob_coordinates.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    element_id = knob_id
                    element_type = 'knob'
                    break
        if not element_id:
            return
        self.cal_drag_pad = element_id
        self.cal_drag_element_type = element_type
        self.cal_drag_start = (x, y)
        self.cal_drag_mode = "move"
        item = self.canvas.find_closest(x, y)
        if item:
            for tag in self.canvas.gettags(item[0]):
                if tag.startswith("resize_"):
                    self.cal_drag_mode = tag
                    break

    def _on_canvas_drag(self, event):
        if not self.calibrate_mode or not self.cal_drag_pad:
            return
        coords_dict = self.coordinates if self.cal_drag_element_type == 'pad' else self.knob_coordinates
        x1, y1, x2, y2 = coords_dict[self.cal_drag_pad]
        dx = event.x - self.cal_drag_start[0]
        dy = event.y - self.cal_drag_start[1]
        if self.cal_drag_mode == 'move':
            x1 += dx; x2 += dx; y1 += dy; y2 += dy
        elif self.cal_drag_mode == 'resize_nw':
            x1 += dx; y1 += dy
        elif self.cal_drag_mode == 'resize_ne':
            x2 += dx; y1 += dy
        elif self.cal_drag_mode == 'resize_sw':
            x1 += dx; y2 += dy
        elif self.cal_drag_mode == 'resize_se':
            x2 += dx; y2 += dy
        if x2 - x1 < 15: x2 = x1 + 15
        if y2 - y1 < 15: y2 = y1 + 15
        coords_dict[self.cal_drag_pad] = (x1, y1, x2, y2)
        self.cal_drag_start = (event.x, event.y)
        self._draw_calibration_rects()

    def _on_canvas_release(self, event):
        self.cal_drag_pad = None
        self.cal_drag_mode = None
        self.cal_drag_element_type = None
        self.cal_drag_start = None

    def _flash_pad_on(self, key):
        if key in self.coordinates and key not in self.active_leds:
            x1, y1, x2, y2 = self.coordinates[key]
            fill = self.canvas.create_rectangle(x1, y1, x2, y2,
                fill="red", stipple="gray50", outline="", tags=f"led_{key}")
            glow = self.canvas.create_rectangle(x1-2, y1-2, x2+2, y2+2,
                outline="#ff4400", width=4, tags=f"led_{key}")
            self.active_leds[key] = [fill, glow]

    def _flash_pad_off(self, key):
        if key in self.active_leds:
            for item in self.active_leds[key]:
                self.canvas.delete(item)
            del self.active_leds[key]

    def _flash_knob_on(self, key, value=None):
        if key in self.knob_coordinates and key not in self.active_knob_leds:
            x1, y1, x2, y2 = self.knob_coordinates[key]
            cx = (x1+x2)/2; cy = (y1+y2)/2; r = (x2-x1)/2
            glow1 = self.canvas.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4,
                outline="#00ffff", width=3, tags=f"knob_led_{key}")
            fill = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                fill="#00ffff", stipple="gray50", outline="", tags=f"knob_led_{key}")
            items = [glow1, fill]
            if value is not None:
                text = self.canvas.create_text(cx, cy, text=str(value),
                    fill="#000000", font=("",8,"bold"), tags=f"knob_led_{key}")
                items.append(text)
            self.active_knob_leds[key] = items
            if key in self._knob_timer_ids:
                self.root.after_cancel(self._knob_timer_ids[key])
            self._knob_timer_ids[key] = self.root.after(300, lambda k=key: self._flash_knob_off(k))
            btn = self.knob_btns.get(key)
            if btn:
                idx = int(key[1:]) + 1
                cfg = self.cfg.get(key, {})
                lbl = cfg.get("label", f"MANOPOLA {idx}")
                btn.config(bg="#00ffff", fg="#000000",
                           text=f"🎛️ {value if value else 'CLICK'}\n{lbl}",
                           relief="raised", bd=3)

    def _flash_knob_off(self, key):
        if key in self.active_knob_leds:
            for item in self.active_knob_leds[key]:
                self.canvas.delete(item)
            del self.active_knob_leds[key]
        self._refresh_btn(key)

    def _flash_knob_move(self, key, current_val):
        self._flash_knob_on(key, current_val)

    def _sel(self, key, display_name):
        old = self.selected
        self.selected = key
        cfg = self.cfg.get(key, {})
        self._sel_lbl.config(text=f"Selezionato: {display_name}", fg="#4a90d9")
        self._name.set(cfg.get("label", ""))
        self._action.set(cfg.get("action", "— nessuna —"))
        self._val.set(cfg.get("value", ""))
        self._on_action()
        self._ok_btn.config(state="normal")
        self._del_btn.config(state="normal")
        self._learn_btn.config(state="normal")
        if old: self._refresh_btn(old)
        self._refresh_btn(key)

    def _on_action(self, *_):
        a = self._action.get()
        self._browse_btn.pack_forget()
        self._record_btn.pack_forget()
        self._val_entry.config(state="normal")
        is_trimmer = "Trimmer:" in a
        is_shortcut = a in ("Shortcut tastiera", "Discord: muto/unmuto", "Discord: deafen/undeafen")
        if is_trimmer and self.selected and self.selected.startswith("p"):
            self._help.config(text="⚠️ I PAD non supportano movimenti rotativi Trimmer.", fg="#e74c3c")
        else:
            self._help.config(text="")
        if a == "— nessuna —" or is_trimmer:
            self._val_entry.config(state="disabled")
        elif a == "Apri applicazione":
            self._browse_btn.pack(side="left", padx=2)
        elif is_shortcut:
            self._val_entry.config(state="readonly")
            self._record_btn.pack(side="left", padx=2)

    def _record_shortcut(self):
        res = KeyRecorder.ask(self.root, self._val.get())
        if res is not None:
            self._val.set(res)

    def _browse(self):
        p = filedialog.askopenfilename()
        if p:
            self._val.set(p)

    def _apply(self):
        if not self.selected:
            return
        a = self._action.get()
        v = self._val.get().strip()
        lbl = self._name.get().strip() or a
        self.cfg[self.selected] = {"label": lbl, "action": a, "value": v}
        self._save_profiles()
        self._refresh_btn(self.selected)
        self._log(f"Assegnato {self.selected} → {lbl} [{self.current_profile}]")

    def _remove(self):
        if not self.selected:
            return
        self.cfg.pop(self.selected, None)
        self._save_profiles()
        self._refresh_btn(self.selected)
        self._sel(self.selected, self.selected)

    def _toggle_learn(self):
        if self.learn:
            self.learn = False
            self._learn_btn.config(text="🎯 Mappatura MIDI (Learn)", bg="#e67e22")
        else:
            if not self.selected:
                return
            self.learn = True
            if self.selected.startswith("p"):
                self._learn_btn.config(text="In ascolto... Premi il PAD fisico", bg="#c0392b")
            else:
                self._learn_btn.config(text="In ascolto... Ruota la MANOPOLA fisica", bg="#c0392b")

    def _start_midi(self):
        if not MIDI_OK:
            return
        pmidi.init()
        devs = []
        for i in range(pmidi.get_count()):
            info = pmidi.get_device_info(i)
            if info[2]:
                devs.append(info[1].decode("utf-8", "replace"))
        self._dcb["values"] = devs
        if devs:
            pref = [n for n in devs if "MPD" in n.upper() or "AKAI" in n.upper()]
            self._dev.set(pref[0] if pref else devs[0])
            self._connect_device()

    def _connect_device(self):
        name = self._dev.get()
        for i in range(pmidi.get_count()):
            info = pmidi.get_device_info(i)
            if info[2] and info[1].decode("utf-8", "replace") == name:
                self.running = False
                self.running = True
                self.midi_thread = threading.Thread(target=self._midi_loop, args=(i, name), daemon=True)
                self.midi_thread.start()

    def _midi_loop(self, dev_id, dev_name):
        try:
            port = pmidi.Input(dev_id)
            self.root.after(0, lambda: self._status(True, f"Connesso a: {dev_name}"))
            while self.running:
                if port.poll():
                    for ev in port.read(64):
                        self.root.after(0, lambda e=ev: self._handle_safe_midi(e))
                time.sleep(0.001)
            port.close()
        except Exception as e:
            self.root.after(0, lambda: self._status(False, f"Errore: {e}"))

    def _handle_safe_midi(self, ev):
        status, d1, d2 = ev[0][0] & 0xF0, ev[0][1], ev[0][2]

        if status == 0x90 and d2 > 0:
            if self.learn and self.selected and self.selected.startswith("p"):
                for k in [k for k, v in self.note_map.items() if v == self.selected]:
                    del self.note_map[k]
                self.note_map[d1] = self.selected
                self.learn = False
                self._learn_btn.config(text="🎯 Mappatura MIDI (Learn)", bg="#e67e22")
                self._log(f"✅ Learn PAD: nota {d1} → {self.selected}")
                self._save_profiles()
                return
            key = self.note_map.get(d1)
            if key:
                self._flash_pad_on(key)
                if key in self.cfg:
                    self._exec_pad(key)

        elif status == 0x80 or (status == 0x90 and d2 == 0):
            key = self.note_map.get(d1)
            if key:
                self._flash_pad_off(key)

        elif status == 0xB0:
            if self.learn and self.selected and self.selected.startswith("k"):
                for cc, k_id in list(KNOB_CCS.items()):
                    if k_id == self.selected:
                        del KNOB_CCS[cc]
                KNOB_CCS[d1] = self.selected
                self.learn = False
                self._learn_btn.config(text="🎯 Mappatura MIDI (Learn)", bg="#e67e22")
                self._log(f"✅ Learn KNOB: CC {d1} → {self.selected}")
                self._save_knob_cc_map()
                self._save_profiles()
                return

            k = KNOB_CCS.get(d1)
            if k:
                self._flash_knob_move(k, d2)
                if k in self.cfg:
                    last_val = self.knob_vals.get(k, d2)
                    self.knob_vals[k] = d2
                    delta = d2 - last_val
                    if d2 == 127: delta = 4
                    elif d2 == 0: delta = -4
                    if delta != 0:
                        self._exec_knob(k, delta, max(1, min(10, abs(delta))))

    def _exec_pad(self, key):
        cfg = self.cfg.get(key, {})
        action, value = cfg.get("action", "— nessuna —"), cfg.get("value", "")
        now = time.time()
        if now - self.last_trig.get(key, 0) < 0.20:
            return
        self.last_trig[key] = now
        try:
            self._log(f"🔥 PAD: {cfg.get('label')} ({key.upper()}) [{self.current_profile}]")
            if action in ("Shortcut tastiera", "Discord: muto/unmuto", "Discord: deafen/undeafen"):
                _press_hotkey(value)
            elif action == "Apri applicazione":
                if sys.platform == "win32": os.startfile(value)
                else: subprocess.Popen(value, shell=True)
            elif action == "Esegui comando":
                subprocess.Popen(value, shell=True)
            elif action == "Spotify: play/pausa":
                _press_media("playpause")
            elif action == "Spotify: prossimo":
                _press_media("nexttrack")
            elif action == "Spotify: precedente":
                _press_media("prevtrack")
        except Exception as e:
            self._log(f"Errore: {e}")

    def _exec_knob_click(self, key):
        cfg = self.cfg.get(key, {})
        action, value = cfg.get("action", "— nessuna —"), cfg.get("value", "")
        try:
            self._log(f"🖱️ KNOB CLICK: {cfg.get('label')} ({key.upper()}) [{self.current_profile}]")
            if action in ("Shortcut tastiera", "Discord: muto/unmuto", "Discord: deafen/undeafen"):
                _press_hotkey(value)
            elif action == "Apri applicazione":
                if sys.platform == "win32": os.startfile(value)
                else: subprocess.Popen(value, shell=True)
            elif action == "Esegui comando":
                subprocess.Popen(value, shell=True)
            elif action == "Spotify: play/pausa":
                _press_media("playpause")
            elif action == "Spotify: prossimo":
                _press_media("nexttrack")
            elif action == "Spotify: precedente":
                _press_media("prevtrack")
        except Exception as e:
            self._log(f"Errore: {e}")

    def _exec_knob(self, key, delta, repeats):
        cfg = self.cfg.get(key, {})
        action = cfg.get("action", "— nessuna —")
        try:
            self._log(f"🎛️ KNOB ROTATE: {cfg.get('label')} ({key.upper()}) delta={delta} [{self.current_profile}]")
            if action == "Trimmer: Volume OS (Su/Giù)":
                _press_media("volumeup" if delta > 0 else "volumedown", repeats)
            elif action == "Trimmer: Player Video YouTube/VLC":
                _press_hotkey("right" if delta > 0 else "left", repeats)
            elif action == "Trimmer: Scorrimento Pagine":
                _press_hotkey("down" if delta > 0 else "up", repeats)
        except Exception as e:
            self._log(f"Errore: {e}")

    def _status(self, ok, text):
        self._dot.config(fg="#27ae60" if ok else "#e74c3c")
        self._slbl.config(text=text)

    def _log(self, msg):
        self._log_w.config(state="normal")
        self._log_w.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self._log_w.see("end")
        self._log_w.config(state="disabled")

    def _refresh_profile_combo(self):
        if hasattr(self, '_profile_combo'):
            profiles = list(self.profiles.keys())
            self._profile_combo['values'] = profiles
            self._profile_combo_var.set(self.current_profile)

    def _on_profile_combo_select(self, event):
        name = self._profile_combo_var.get()
        if name and name != self.current_profile:
            self._switch_profile(name)

    def _import(self):
        p = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not p:
            return
        try:
            data = json.loads(Path(p).read_text())
            if "profiles" in data:
                self.profiles = data.get("profiles", {})
                self.profile_assignments = data.get("assignments", {})
                self.current_profile = data.get("current", "inverted")
                if self.current_profile in self.profiles:
                    profile_data = self.profiles[self.current_profile]
                    note_map_raw = profile_data.get("note_map", {})
                    self.note_map = {int(k): v for k, v in note_map_raw.items()} if note_map_raw else dict(DEFAULT_NOTES)
                    self.cfg = profile_data.get("cfg", {})
            else:
                self.note_map = {int(k): v for k, v in data.pop("_nmap", {}).items()}
                self.cfg = data
                self.profiles["inverted"] = {"note_map": {str(k): v for k, v in self.note_map.items()}, "cfg": dict(self.cfg)}
            self._load_knob_cc_map()
            self._refresh_profile_combo()
            self._update_profile_indicator()
            self._refresh_all_assignments()
            self._save_profiles()
            self._log("Configurazione importata.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def _export(self):
        p = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not p:
            return
        self.profiles[self.current_profile] = {"note_map": {str(k): v for k, v in self.note_map.items()}, "cfg": dict(self.cfg)}
        self._save_knob_cc_map()
        data = {"profiles": self.profiles, "assignments": self.profile_assignments, "current": self.current_profile}
        Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False))
        self._log("Configurazione esportata.")


if __name__ == "__main__":
    if not MIDI_OK:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Dipendenza mancante",
                             "Installa pygame:\n\npython -m pip install pygame pyautogui pillow pynput")
        sys.exit(1)
    import pygame
    pygame.init()
    pmidi.init()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    pmidi.quit()
    pygame.quit()