# Pro IPTV Player (Vavoo Edition)

A modern, standalone desktop IPTV player built with Python and Qt6, designed to work seamlessly with Vavoo streams.

## Features
- **Vavoo Integration:** Automatically fetches and authenticates streams securely.
- **Smart EPG:** Merged guide data from Italy and Switzerland sources (including RSI LA 1/2).
- **Native Player:** VLC-based playback engine for high performance.
- **Modern UI:** Dark mode interface with channel search, bouquets (TV Sat, Sport, Cinema), and favorites.
- **Switzerland Support:** Specialized handling for RSI channels with correct EPG mapping.

## Installation

### Prerequisites
- Python 3.10+
- VLC Media Player (must be installed on the system)

### Setup
1. **Clone/Download** this repository.
2. **Install dependencies**:
   ```powershell
   # Windows
   python -m venv .venv
   .\.venv\Scripts\minstall -r python_iptv/requirements.txt
   ```

## Usage
Run the player using the internal script:

```powershell
.\.venv\Scripts\python python_iptv/main.py
```

The player will:
1. Generate/Update the playlist (`ITALIA.m3u8`).
2. Launch the GUI.
3. Load the latest EPG data in the background.

## Directory Structure
- `python_iptv/`: Main application source code.
- `logos/`: Channel logos (auto-downloaded).
- `ITALIA.m3u8`: Generated playlist file.
- `vavoo_player.log`: Debug logs.

## Troubleshooting
- **VLC Error:** Ensure VLC is installed (64-bit if using 64-bit Python).
- **Missing Channels:** Click the "Refresh" button in the player settings to force a playlist update.
