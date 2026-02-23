# Antigravity System Instructions & Memory Log

## 1. Project Overview

* **Name:** Vavoo IPTV Playlist Generator
* **Scope:** Automated M3U8 playlist generation for Italian IPTV channels from Vavoo sources
* **Stack:** Python 3, `requests`, `tzdata`
* **Deployment:** GitHub Actions (daily auto-generation)

## 2. Architecture

* `generate_playlist_cli.py` — CLI entry point
* `playlist_generator.py` — Core generator (channel fetching, EPG mapping, M3U8 output)
* `epg_manager.py` — EPG data fetching and caching (XMLTV format)
* `data_manager.py` — Logo management and EPG name resolution

## 3. Key Decisions

* **Groups:** Only `Italy` is fetched by default
* **EPG Sources:** `iptv-epg.org` (primary) + `epgshare01.online` (backup)
* **HISTORY channels:** `.c` and `.s` suffixes are normalized and all variants display as "HISTORY"
* **NOVE:** Uses `Nove.it` EPG ID (verified from `epg_ripper_IT1.txt`)
* **Channel ordering:** Follows Tivùsat numbering (`TIVUSAT_ORDER` dict)

## 4. Persistent Memory Log

* **2026-02-23:** Optimized codebase — removed PyQt6 Player, Xtream API server, and all unused dependencies. Only playlist generator remains.
* **2026-02-23:** Fixed HISTORY EPG mapping (double-space normalization bug) and updated NOVE to `Nove.it`.
* **2026-02-23:** Restricted GROUPS to Italy only.
