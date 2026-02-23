# 📺 Vavoo IPTV Playlist Generator

Generatore automatico di playlist M3U8 per canali IPTV italiani da sorgenti Vavoo, con mapping EPG completo e loghi.

## ✨ Key Features

- **Generazione automatica** della playlist M3U8 con canali italiani
- **Mapping EPG** completo da `iptv-epg.org` e `epgshare01.online`
- **Loghi** per tutti i canali principali (RAI, Mediaset, Sky, DAZN, etc.)
- **Categorizzazione** intelligente: TV Sat, Cinema, Sport, Kids, News, Documentary
- **GitHub Actions** — la playlist si aggiorna automaticamente ogni giorno
- **Ordinamento Tivùsat** — i canali seguono la numerazione ufficiale

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
--xc-output PATH    Generate XCIPTV-compatible playlist
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
