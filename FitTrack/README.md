# FitTrack // Quantum Biometric HUD 🩺⚡

> **Real-Time Panoramic Biometric HUD & Health Record Console**  
> An ultra-unique, production-grade Windows desktop application built with Python and Tkinter, featuring a 3-wing cockpit, 240° canvas radial gauge, live bio-avatar radar, and interactive dual-slider controls.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-blueviolet)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Cockpit Architecture

| Left Wing (Telemetry Terminal) | Center Core (Radial HUD & Avatar) | Right Wing (Waveforms & Analytics) |
|---|---|---|
| Dual numeric + live interactive cyber sliders, quick bio-presets, and action command array | 240° sweeping radial gauge, animated needle, holographic bio-avatar, and BMR/BSA telemetry matrix | Dark cyberpunk oscilloscope trendline and segmented category distribution spectrum |

---

## Features

| Category | Capabilities |
|---|---|
| **Radial HUD Gauge** | Custom canvas 240° circular gauge with ease-out needle animation, WHO color zones, and central digital display |
| **Bio-Avatar Matrix** | Wireframe holographic human silhouette with continuous vertical radar beam and vital telemetry beacons |
| **Dual Control Inputs** | Precision numeric entry synchronized with real-time cybernetic sliders for Height and Weight |
| **Biometric Telemetry** | BMR (Mifflin-St Jeor kcal/day), BSA (Mosteller m²), Target Weight Delta, and holographic clinical advisory |
| **Quick Presets** | Instant 1-click loading for Athlete, Standard, Youth, and Power profiles |
| **Oscilloscope Charts** | Dark cyberpunk oscilloscope line trend with glowing markers + category distribution spectrum |
| **Records Matrix** | Full CRUD, real-time name filter, sortable columns, and instant HUD reflection on row selection |
| **Themes** | **Cyber Obsidian HUD** (Deep space obsidian with neon cyan/emerald) and **Titanium Bio-Lab** (Crisp medical sci-fi light mode) |
| **Shortcuts** | `Ctrl+S` Compute & Save · `Ctrl+N` Clear · `Delete` Delete record · `Return` Submit |
| **Splash Screen** | Cyberpunk animated splash screen with neon corner brackets and biometric loading telemetry |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/vasiharan/fittrack.git
cd fittrack

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
cd FitTrack
python main.py
```

### Dependencies

```
matplotlib>=3.7
Pillow>=9.0
```

> **Note:** Tkinter and SQLite3 are bundled with the Python standard library — no extra install needed.

---

## Project Structure

```
BMI calculator/
├── FitTrack/                   # Main application package
│   ├── main.py                 # Entry point — splash screen, window setup
│   ├── requirements.txt        # pip dependencies
│   ├── LICENSE                 # MIT License
│   ├── README.md               # This file
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py               # SQLite DatabaseManager (CRUD + statistics + search)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── person.py           # HealthRecord dataclass
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bmi_service.py      # BMI calculation, status, suggestions
│   │   ├── validator.py        # InputValidator with ValidationError
│   │   └── export_service.py   # CSV export logic
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── styles.py           # Design tokens, fonts, widget factories, animations
│   │   ├── table.py            # HealthRecordTable (Treeview + empty states)
│   │   ├── dialogs.py          # AlertDialog · ConfirmDialog · SettingsDialog
│   │   └── dashboard.py        # FitTrackDashboard — main application frame
│   │
│   └── assets/
│       ├── logo.png            # Auto-generated app icon (64×64, requires Pillow)
│       ├── icons/              # Reserved for future icon assets
│       └── screenshots/        # Reserved for documentation screenshots
│
└── showcase.py                 # Before/After interactive comparison launcher
```

---

## Architecture

FitTrack Enterprise follows the **Model-View-Controller (MVC)** pattern:

```
┌─────────────────────────────────────────┐
│                  main.py                │  Bootstrap, splash, root window
└─────────────┬───────────────────────────┘
              │
    ┌─────────▼──────────┐
    │   FitTrackDashboard │  Controller + View (ui/dashboard.py)
    └────┬──────┬────────┘
         │      │
  ┌──────▼──┐  ┌▼──────────────┐
  │ UI Layer│  │ Service Layer  │
  │ table   │  │ bmi_service    │  Business Logic
  │ dialogs │  │ validator      │
  │ styles  │  │ export_service │
  └─────────┘  └───────┬────────┘
                        │
              ┌─────────▼──────────┐
              │   DatabaseManager   │  SQLite persistence
              └─────────────────────┘
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + S` | Calculate BMI and save new record |
| `Ctrl + N` | Clear form and deselect |
| `Delete`   | Delete selected record |
| `Return`   | Submit form when a field is focused |
| `Tab`      | Move focus forward through fields |
| `Shift+Tab`| Move focus backward |
| `Escape`   | Close any open dialog |

---

## Before / After Showcase

To compare the original prototype with the enterprise version:

```bash
# Run from the BMI calculator/ folder (parent of FitTrack/)
python showcase.py
```

This opens a dark-themed launcher with:
- **BEFORE** — the original minimal BMI calculator (no DB, no validation)
- **AFTER**  — the full FitTrack Enterprise application
- Project stats (modules, lines of code, features added)
- Improvement metrics table

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**vasiharan** · © 2026
