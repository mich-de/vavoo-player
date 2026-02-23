# 📺 Vavoo IPTV Playlist Generator

Automated M3U8 playlist generator for Italian IPTV channels from Vavoo sources, with full EPG mapping and logos.

## ✨ Features

- **Automated generation** of M3U8 playlists with Italian channels
- **Full EPG mapping** from `iptv-epg.org` and `epgshare01.online`
- **Channel logos** for all major networks (RAI, Mediaset, Sky, DAZN, etc.)
- **Smart categorization**: TV Sat, Cinema, Sport, Kids, News, Documentary
- **GitHub Actions** — the playlist is auto-updated daily
- **Tivùsat ordering** — channels follow the official numbering

## 🚀 Quick Start

### Windows (start.bat)

```batch
git clone https://github.com/mich-de/vavoo-player.git
cd vavoo-player
start.bat
```

### Manual

```bash
cd python_iptv
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python generate_playlist_cli.py --output ../playlist.m3u8
```

### CLI Options

```
--output PATH       Output file path (default: playlist.m3u8)
--groups GROUP...   Groups to include (default: Italy)
```

## 📁 Project Structure

```
vavoo-player/
├── .github/workflows/     GitHub Actions (auto-generation)
├── logos/                  Channel logos (PNG/SVG)
├── python_iptv/
│   ├── generate_playlist_cli.py   CLI entry point
│   ├── requirements.txt
│   └── src/
│       ├── playlist_generator.py  Core generator
│       ├── epg_manager.py         EPG data management
│       └── data_manager.py        Channel & logo management
├── playlist.m3u8           Generated playlist
└── start.bat               Windows launcher
```

## 📡 EPG Sources

| Source | URL |
|--------|-----|
| Primary IT | `iptv-epg.org/files/epg-it.xml.gz` |
| Primary CH | `iptv-epg.org/files/epg-ch.xml.gz` |
| Backup IT | `epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz` |
| Backup CH | `epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz` |

## 📜 License

For personal use only.
