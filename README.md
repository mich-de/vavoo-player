# 📺 Vavoo Pro IPTV Player

> [!WARNING]
> **Educational Purpose Only:** This project is provided strictly for educational and research purposes. Use of this software for any other purpose is strongly discouraged. The authors are not responsible for how this software is used.

A modern, standalone desktop IPTV player built with **Python and PyQt6**, specifically designed to dynamically fetch, authenticate, and play streams natively supporting Italian and Swiss networks with rich EPG integrations.

---

## ✨ Key Features

- **Automated Integration**: Seamlessly connects, handshakes, and fetches the latest channels securely.
- **Smart EPG & Local Logos**: Real-time programming guide with progress bars. Automatically merges and maps EPG data for Italy and Switzerland.
- **Auto-updating CI Pipeline**: A GitHub Action automatically fetches the latest streams and generates the updated `playlist.m3u8` directly in the repository on a regular schedule.
- **Dual-Engine Player**: Built-in support for both **VLC** and **mpv** backends (auto-detects the best available engine).
- **Modern Dark UI**: A sleek, user-friendly interface featuring:
  - Global channel search.
  - Organized bouquets (TV Sat, Sport, Cinema, Documentary, News).
  - Quick favorites management.
- **Advanced Channel Mapping**: Specific mapping for documentary networks (including HISTORY `.c` and `.s`) and Swiss RSI channels.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **VLC Media Player** or **mpv Player** installed on your system.

### One-Click Installation (Windows)

The simplest way to run the application on Windows is using the provided batch script. It automatically handles the virtual environment and dependency installation.

1. Clone or download this repository.
2. Double-click on `start.bat`.

*That's it! The script will create a Python virtual environment, install the required packages, and launch the player.*

---

## 🛠️ Manual Installation & Usage

If you prefer to install it manually or are not on Windows:

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r python_iptv/requirements.txt
   ```

3. **Run the player:**

   ```bash
   python python_iptv/main.py
   ```

---

## 📁 Project Structure

- `python_iptv/` - Main PyQt6 application and backend logic.
  - `src/playlist_generator.py` - Core engine for authentication and channel harvesting.
- `logos/` - Locally cached channel logos.
- `.github/workflows/` - GitHub Actions for automated playlist generation.
- `playlist.m3u8` - The automatically generated master playlist.
- `start.bat` - Windows rapid launcher.

---

## ❓ Troubleshooting

- **Player doesn't start / Video error:** Ensure you have VLC installed (and you are using the correct 64-bit version matching your Python architecture).
- **Missing or outdated channels:** The repository automatically updates the `playlist.m3u8`, but if you want to force an update locally, you can click the "Refresh" button inside the player's settings.
