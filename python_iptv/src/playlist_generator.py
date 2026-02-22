import requests
import json
import time
import os
import sys
import logging
import logging
import urllib3
# Add parent dir to sys.path to resolve data_manager if needed
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.data_manager import DataManager

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONSTANTS ---
USER_AGENT = "okhttp/4.11.0"
API_BASE = "https://www.vavoo.tv/api"
VAOO_URL = "https://vavoo.to/mediahubmx-catalog.json"

GROUPS = [
    "Germany", "Italy", "France", "Spain", "Portugal", 
    "Turkey", "Balkan", "Albania", "Arabia", "Russia", 
    "Poland", "Greece", "USA", "Latino", "Vavoo", "Switzerland"
]

TIVUSAT_ORDER = {
    "RAI 1": 1, "RAI 2": 2, "RAI 3": 3, "RETE 4": 4, "CANALE 5": 5, "ITALIA 1": 6, "LA7": 7, "TV8": 8, "NOVE": 9,
    "RAI 4": 10, "IRIS": 11, "LA5": 12, "RAI 5": 13, "RAI MOVIE": 14, "RAI PREMIUM": 15, 
    "MEDIASET EXTRA": 17, "TV2000": 18, "CIELO": 19, "20 MEDIASET": 20, "RAI SPORT": 21,
    "IRIS": 22, "RAI STORIA": 23, "RAI NEWS 24": 24, "TGCOM24": 25, "DMAX": 26, "REAL TIME": 31,
    "CINE34": 34, "FOCUS": 35, "RTL 102.5": 36, "WARNER TV": 37, "GIALLO": 38, "TOP CRIME": 39,
    "BOING": 40, "K2": 41, "RAI GULP": 42, "RAI YOYO": 43, "FRISBEE": 44, "CARTOONITO": 46, "SUPER!": 47,
    "SPIKE": 49, "SKY TG24": 50, "TGCOM24": 51, "DMAX": 52, "ITALIA 2": 66, "RADIO ITALIA TV": 70
}

BOUQUETS = {
    "TV Sat": ["RAI 1", "RAI 2", "RAI 3", "RETE 4", "CANALE 5", "ITALIA 1", "LA7", "TV8", "NOVE", "20 MEDIASET", "RAI 4", "IRIS", "LA5", "RAI 5", "RAI MOVIE", "RAI PREMIUM", "RAI GULP", "RAI YOYO", "RAI STORIA", "RAI SCUOLA", "RAI NEWS 24", "RAI SPORT", "SPORTITALIA", "TV2000", "CIELO", "DMAX", "REAL TIME", "QVC", "RTL 102.5", "RADIO ITALIA TV", "BOING", "K2", "FRISBEE", "CARTOONITO", "SUPER!", "SPIKE", "PARAMOUNT", "CINE34", "FOCUS", "TOP CRIME", "GIALLO", "TGCOM24", "VH1", "ITALIA 2", "SUPERTENNIS", "MOTOR TREND", "RAI 4K", "RSI LA 1", "RSI LA 2"],
    "Cinema": ["SKY CINEMA", "PREMIUM CINEMA"],
    "Sport": ["SKY SPORT", "DAZN", "EUROSPORT", "TENNIS", "MOTOGP", "F1", "CALCIO", "INTER", "MILAN", "JUVE"],
    "Documentary": ["SKY DOCUMENTARIES", "SKY NATURE", "GEO", "DISCOVERY"],
    "News": ["SKY TG24", "EURONEWS", "BBC", "CNN", "CNBC"]
}

# Mapping from Normalized Vavoo Name to EPG ID
# Based on common Italian XMLTV IDs
EPG_MAP = {
    "RAI 1": "Rai 1.it",
    "RAI 2": "Rai 2.it",
    "RAI 3": "Rai 3.it",
    "RAI 4": "Rai 4.it",
    "RAI 4K": "Rai 4k.it",
    "RAI 5": "Rai 5.it",
    "RAI MOVIE": "Rai Movie.it",
    "RAI PREMIUM": "Rai Premium.it",
    "RAI GULP": "Rai Gulp.it",
    "RAI YOYO": "Rai Yoyo.it",
    "RAI STORIA": "Rai Storia.it",
    "RAI SCUOLA": "Rai Scuola.it",
    "RAI NEWS 24": "RaiNews24.it",
    "RAI SPORT": "Rai Sport + HD.it",
    "CANALE 5": "Canale 5.it",
    "ITALIA 1": "Italia 1.it",
    "ITALIA 2": "Italia 2.it",
    "RETE 4": "Rete 4.it",
    "LA7": "La7.it",
    "LA7D": "La7d.it",
    "TV8": "TV8.it",
    "NOVE": "Nove.it",
    "DISCOVERY NOVE": "Nove.it",
    "20 MEDIASET": "20.it",
    "CIELO": "Cielo.it",
    "DMAX": "DMAX.it",
    "REAL TIME": "Real Time.it",
    "FOCUS": "Focus.it",
    "DISCOVERY FOCUS": "Focus.it",
    "GIALLO": "Giallo.it",
    "TOP CRIME": "Top Crime.it",
    "BOING": "Boing.it",
    "BOING PLUS": "Boing Plus.it",
    "K2": "K2.it",
    "DISCOVERY K2": "K2.it",
    "FRISBEE": "Frisbee.it",
    "CARTOONITO": "Cartoonito.it",
    "SUPER!": "Super!.it",
    "IRIS": "Iris.it",
    "LA5": "La 5.it",
    "CINE34": "Cine34.it",
    "MEDIASET EXTRA": "Mediaset Extra.it",
    "TGCOM24": "Tgcom24.it",
    "20": "20.it",
    "ACI SPORT TV": "ACI Sport Tv.it",
    "AL JAZEERA": "Al Jazeera.it",
    "ALMA TV": "Alma TV.it",
    "BABY TV": "Baby TV.it",
    "BBC WORLD NEWS": "BBC World News.it",
    "BIKE": "Bike.it",
    "BLAZE": "Blaze.it",
    "BLOOMBERG": "Bloomberg.it",
    "BOOMERANG + 1": "Boomerang + 1.it",
    "BOOMERANG": "Boomerang.it",
    "CACCIA E PESCA": "Caccia e Pesca.it",
    "CARTOON NETWORK": "Cartoon Network.it",
    "CLASS-CNBC": "Class-Cnbc.it",
    "CLASSICA HD": "Classica HD.it",
    "CN +1": "CN +1.it",
    "CNBC": "CNBC.it",
    "CNN INTL": "CNN Intl.it",
    "COMEDY +1": "Comedy +1.it",
    "COMEDY CENTRAL": "Comedy Central.it",
    "CRIME+ INV.": "Crime+ Inv..it",
    "DAZN": "DAZN.it",
    "DAZN 1": "DAZN.it",
    "DAZN 2": "DAZN.it",
    "DEA JUNIOR": "DeA Junior.it",
    "DEAKIDS": "DeAKids.it",
    "DEAKIDS+1": "DeAKids+1.it",
    "DEEJAY TV": "Deejay TV.it",
    "DISCOVERY CH +1": "Discovery Ch +1.it",
    "DISCOVERY CHANNEL HD": "Discovery Channel HD.it",
    "DISCOVERY SCIENCE HD": "Discovery Science HD.it",
    "DMAX HD": "DMAX HD.it",
    "DONNATV": "DonnaTv.it",
    "EQUTV": "Equtv.it",
    "ER24 - EMILIA ROMAGNA 24": "Er24 - Emilia Romagna 24.it",
    "EURONEWS": "Euronews.it",
    "EUROSPORT 2HD": "Eurosport 2HD.it",
    "EUROSPORT HD": "Eurosport HD.it",
    "EXPLORER HD CHANNEL": "Explorer Hd channel.it",
    "FASHION TV": "Fashion TV.it",
    "FOODNETWORK": "FoodNetwork.it",
    "FOX +1": "Fox +1.it",
    "FOX BUSINESS": "Fox Business.it",
    "FOX HD": "Fox HD.it",
    "FOX NEWS": "Fox News.it",
    "FRANCE 24 ENGLISH": "France 24 English.it",
    "FRANCE 24": "France 24.it",
    "GAMBERO ROSSO HD": "Gambero Rosso HD.it",
    "HGTV - HOMEANDGARDEN": "HGTV - HomeandGarden.it",
    "HISTORY 1": "History 1.it",
    "HISTORY HD": "History HD.it",
    "HORSE TV HD": "Horse TV HD.it",
    "I24NEWS": "I24news.it",
    "IL61": "IL61.it",
    "INTER TV HD": "Inter TV HD.it",
    "ITALIA 7 GOLD": "Italia 7 Gold.it",
    "LA 1": "La 1.it",
    "LA 2": "La 2.it",
    "LAZIO STYLE CHANNEL": "Lazio Style Channel.it",
    "MARCOPOLO TRAVEL TV": "Marcopolo Travel TV.it",
    "MILAN TV": "Milan TV.it",
    "MOTOR TREND HD": "Motor Trend HD.it",
    "MTV MUSIC": "Mtv Music.it",
    "MTV": "MTV.it",
    "NAT GEO WILD +1": "Nat Geo Wild +1.it",
    "NATIONAL GEO HD": "National Geo HD.it",
    "NATIONAL GEOGRAPHIC WILD": "National Geographic Wild.it",
    "NATIONALGEO +1": "NationalGeo +1.it",
    "NHK WORLD TV": "NHK World TV.it",
    "NICK JR+1": "Nick Jr+1.it",
    "NICK JUNIOR": "Nick Junior.it",
    "NICKELODEON + 1": "Nickelodeon + 1.it",
    "NICKELODEON": "Nickelodeon.it",
    "PESCA E CACCIA": "Pesca e Caccia.it",
    "PREMIUM ACTION": "Premium Action.it",
    "PREMIUM CINEMA 1": "Premium Cinema 1.it",
    "PREMIUM CINEMA 2": "Premium Cinema 2.it",
    "PREMIUM CINEMA 3": "Premium Cinema 3.it",
    "PREMIUM CRIME": "Premium Crime.it",
    "PREMIUM STORIES": "Premium Stories.it",
    "PRIMAFILA 1": "Primafila 1.it",
    "PRIMAFILA 2": "Primafila 2.it",
    "PRIMAFILA 3": "Primafila 3.it",
    "PRIMAFILA 4": "Primafila 4.it",
    "PRIMAFILA 5": "Primafila 5.it",
    "QVC": "QVC.it",
    "R101": "R101.it",
    "RADIO 105": "Radio 105.it",
    "RADIO FRECCIA": "Radio Freccia.it",
    "RADIO ITALIA TV": "Radio Italia Tv.it",
    "RADIO MONTE CARLO": "Radio Monte Carlo.it",
    "RADIONORBA TV": "Radionorba TV.it",
    "RT DOC HD": "RT Doc HD.it",
    "RTL 102.5 TV": "RTL 102.5 TV.it",
    "RUSSIA TODAY": "Russia Today.it",
    "SKY ADVENTURE": "Sky Adventure.it",
    "SKY ARTE +1": "Sky Arte +1.it",
    "SKY ARTE HD": "Sky Arte HD.it",
    "SKY ARTE HD-400": "Sky Arte HD-400.it",
    "SKY ATLANTIC +1": "Sky Atlantic +1.it",
    "SKY ATLANTIC HD": "Sky Atlantic HD.it",
    "SKY CINEMA ACTION HD": "Sky Cinema Action HD.it",
    "SKY CINEMA COLLECTION HD": "Sky Cinema Collection HD.it",
    "SKY CINEMA COMEDY HD": "Sky Cinema Comedy HD.it",
    "SKY CINEMA DRAMA HD": "Sky Cinema Drama HD.it",
    "SKY CINEMA DUE +24": "Sky Cinema Due +24.it",
    "SKY CINEMA DUE HD": "Sky Cinema Due HD.it",
    "SKY CINEMA FAMILY HD": "Sky Cinema Family HD.it",
    "SKY CINEMA ROMANCE HD": "Sky Cinema Romance HD.it",
    "SKY CINEMA SUSPENSE HD": "Sky Cinema Suspense HD.it",
    "SKY CINEMA UNO +24": "Sky Cinema Uno +24.it",
    "SKY CINEMA UNO HD": "Sky Cinema Uno HD.it",
    "SKY CRIME": "Sky Crime.it",
    "SKY DOCUMENTARIES +1 HD": "Sky Documentaries +1 HD.it",
    "SKY DOCUMENTARIES HD": "Sky Documentaries HD.it",
    "SKY INVESTIGATION +1 HD": "Sky Investigation +1 HD.it",
    "SKY INVESTIGATION HD": "Sky Investigation HD.it",
    "SKY METEO24": "Sky Meteo24.it",
    "SKY NATURE HD": "Sky Nature HD.it",
    "SKY NEWS": "Sky News.it",
    "SKY SERIE +1 HD": "Sky Serie +1 HD.it",
    "SKY SERIE HD": "Sky Serie HD.it",
    "SKY SPORT 251": "Sky Sport 251.it",
    "SKY SPORT 252": "Sky Sport 252.it",
    "SKY SPORT 253": "Sky Sport 253.it",
    "SKY SPORT 254": "Sky Sport 254.it",
    "SKY SPORT 255": "Sky Sport 255.it",
    "SKY SPORT 256": "Sky Sport 256.it",
    "SKY SPORT 257": "Sky Sport 257.it",
    "SKY SPORT 258": "Sky Sport 258.it",
    "SKY SPORT 259": "Sky Sport 259.it",
    "SKY SPORT 260": "Sky Sport 260.it",
    "SKY SPORT 261": "Sky Sport 261.it",
    "SKY SPORT 4K": "Sky Sport 4K.it",
    "SKY SPORT ACTION": "Sky Sport Action.it",
    "SKY SPORT ARENA": "Sky Sport Arena.it",
    "SKY SPORT CALCIO": "Sky Sport Calcio.it",
    "SKY SPORT F1 HD": "Sky Sport F1 HD.it",
    "SKY SPORT GOLF": "Sky Sport Golf.it",
    "SKY SPORT MOTOGP": "Sky Sport MotoGP.it",
    "SKY SPORT MOTO GP": "Sky Sport MotoGP.it",
    "SKY SPORT NBA": "Sky Sport NBA.it",
    "SKY SPORT TENNIS HD": "Sky Sport Tennis HD.it",
    "SKY SPORT UNO": "Sky Sport Uno.it",
    "SKY SPORT24": "Sky Sport24.it",
    "SKY TG24": "Sky Tg24.it",
    "SKY UNO +1HD": "Sky Uno +1HD.it",
    "SKY UNO HD": "Sky Uno HD.it",
    "SMTV SAN MARINO": "SMtv San Marino.it",
    "SPORTITALIA": "Sportitalia.it",
    "SUPERTENNIS HD": "SuperTennis HD.it",
    "SUPERTENNIS": "SuperTennis.it",
    "TELECAMPIONE": "Telecampione.it",
    "TG NORBA24": "TG Norba24.it",
    "TOP CALCIO 24": "Top Calcio 24.it",
    "TRM H24": "TRM h24.it",
    "TV2000": "TV2000.it",
    "RSI LA 1": "La 1.it",
    "RSI LA 2": "La 2.it",
}

class PlaylistGenerator:
    """
    Handles fetching channels from Vavoo API and generating M3U8 playlists.
    """
    def __init__(self):
        self._auth_cache = {
            "sig": None,
            "timestamp": 0
        }
        self.dm = DataManager()

    def _get_auth_signature(self):
        """Performs handshake to get the addon signature."""
        url = f"{API_BASE}/app/ping"
        headers = {
            "user-agent": USER_AGENT,
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip"
        }
        
        data = {
            "token": "tosFwQCJMS8qrW_AjLoHPQ41646J5dRNha6ZWHnijoYQQQoADQoXYSo7ki7O5-CsgN4CH0uRk6EEoJ0728ar9scCRQW3ZkbfrPfeCXW2VgopSW2FWDqPOoVYIuVPAOnXCZ5g",
            "reason": "app-blur",
            "locale": "de",
            "theme": "dark",
            "metadata": {
                "device": {"type": "Handset", "brand": "google", "model": "Nexus", "name": "21081111RG", "uniqueId": "d10e5d99ab665233"},
                "os": {"name": "android", "version": "7.1.2", "abis": ["arm64-v8a", "armeabi-v7a", "armeabi"], "host": "android"},
                "app": {"platform": "android", "version": "3.1.20", "buildId": "289515000", "engine": "hbc85", "signatures": ["6e8a975e3cbf07d5de823a760d4c2547f86c1403105020adee5de67ac510999e"], "installer": "app.revanced.manager.flutter"},
                "version": {"package": "tv.vavoo.app", "binary": "3.1.20", "js": "3.1.20"}
            },
            "appFocusTime": 0,
            "playerActive": False,
            "playDuration": 0,
            "devMode": False,
            "hasAddon": True,
            "castConnected": False,
            "package": "tv.vavoo.app",
            "version": "3.1.20",
            "process": "app",
            "firstAppStart": 1743962904623,
            "lastAppStart": 1743962904623,
            "ipLocation": "",
            "adblockEnabled": True,
            "proxy": {"supported": ["ss", "openvpn"], "engine": "ss", "ssVersion": 1, "enabled": True, "autoServer": True, "id": "pl-waw"},
            "iap": {"supported": False}
        }

        try:
            logging.info("Requesting authentication signature...")
            # Disable SSL verification
            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            sig = response.json().get("addonSig")
            if sig:
                self._auth_cache["sig"] = sig
                self._auth_cache["timestamp"] = time.time()
                logging.info("Signature received successfully.")
            return sig
        except Exception as e:
            logging.error(f"Error getting auth signature: {e}")
            return None

    def get_signature(self, max_age_seconds=600):
        """Returns a valid signature, refreshing if expired."""
        if self._auth_cache["sig"] and (time.time() - self._auth_cache["timestamp"] < max_age_seconds):
            return self._auth_cache["sig"]
        return self._get_auth_signature()

    def fetch_all_channels(self, target_groups=None):
        """
        Fetches channels from the API.
        
        Args:
            target_groups (list): List of groups to fetch. If None, uses default GROUPS.
            
        Returns:
            list: List of channel dictionaries.
        """
        if target_groups is None:
            target_groups = GROUPS

        sig = self.get_signature()
        if not sig:
            logging.error("Could not obtain signature. Aborting fetch.")
            return []

        all_channels = []
        seen_urls = set()
        
        for group in target_groups:
            logging.info(f"Fetching group: {group}...")
            cursor = 0
            group_items = 0
            
            while True:
                data = {
                    "language": "en",
                    "region": "US",
                    "catalogId": "iptv",
                    "id": "iptv",
                    "adult": False,
                    "search": "",
                    "sort": "name",
                    "filter": {"group": group},
                    "cursor": cursor,
                    "clientVersion": "3.0.2"
                }
                
                headers = {
                    "user-agent": USER_AGENT,
                    "accept": "application/json",
                    "content-type": "application/json; charset=utf-8",
                    "mediahubmx-signature": sig
                }
                
                try:
                    # Disable SSL verification
                    r = requests.post(VAOO_URL, json=data, headers=headers, timeout=15, verify=False)

                    r.raise_for_status()
                    res = r.json()
                    
                    items = res.get("items", [])
                    if not items:
                        break
                        
                    for item in items:
                        url = item.get("url")
                        name = item.get("name")
                        seen_key = (name, url)
                        if url and seen_key not in seen_urls:
                            clean_item = {
                                "name": name,
                                "url": url,
                                "group": group,
                                "logo": item.get("logo")
                            }
                            all_channels.append(clean_item)
                            seen_urls.add(seen_key)
                            group_items += 1
                    
                    cursor = res.get("nextCursor")
                    if cursor is None:
                        break
                        
                except Exception as e:
                    logging.error(f"Error fetching {group}: {e}")
                    break
            
            logging.info(f" > Found {group_items} channels in {group}")

        # Always search for RSI specifically to ensure we catch all variants and groups
        rsi_channels = self.brute_force_search_rsi(sig)
        for rsi_ch in rsi_channels:
            seen_key = (rsi_ch['name'], rsi_ch['url'])
            if seen_key not in seen_urls:
                all_channels.append(rsi_ch)
                seen_urls.add(seen_key)

        return all_channels

    def brute_force_search_rsi(self, sig):
        """Searches specifically for RSI channels in likely groups."""
        target_names = ["RSI LA 1", "RSI LA 2", "RSI LA1", "RSI LA2"]
        found = []
        # Germany and Vavoo are most likely candidates for Swiss content
        search_groups = ["Italy", "Germany", "Vavoo", "Switzerland", "Swiss", "Other"] 
        search_queries = ["RSI LA", "RSI LA 1", "RSI LA 2", "RSI", "LA 1", "LA 2"]
        
        logging.info("Attempting targeted search for RSI channels...")
        
        seen_urls_rsi = set()
        for group in search_groups:
            for query in search_queries:
                cursor = 0
                while True:
                    data = {
                        "language": "en",
                        "region": "US",
                        "catalogId": "iptv",
                        "id": "iptv",
                        "adult": False,
                        "search": query, 
                        "sort": "name",
                        "filter": {"group": group},
                        "cursor": cursor,
                        "clientVersion": "3.0.2"
                    }
                    
                    headers = {
                        "user-agent": USER_AGENT,
                        "accept": "application/json",
                        "content-type": "application/json; charset=utf-8",
                        "mediahubmx-signature": sig
                    }
                    
                    try:
                        r = requests.post(VAOO_URL, json=data, headers=headers, timeout=12, verify=False)
                        if r.status_code == 200:
                            res = r.json()
                            items = res.get("items", [])
                            if not items:
                                break
                            
                            for item in items:
                                name = item.get("name", "")
                                url = item.get("url")
                                
                                if url and url not in seen_urls_rsi:
                                    clean_name_up = name.upper()
                                    if any(tn.upper() in clean_name_up for tn in target_names):
                                        found.append({
                                            "name": name,
                                            "url": url,
                                            "group": "Switzerland", 
                                            "logo": item.get("logo"),
                                            "priority": 100 
                                        })
                                        seen_urls_rsi.add(url) # We still deduplicate URLs locally within this search
                            
                            cursor = res.get("nextCursor")
                            if cursor is None:
                                break
                        else:
                            break
                    except Exception:
                        break
                
        return found



    def _normalize_name(self, name):
        import re
        if not name: return ""
        n = name.upper()
        n = re.sub(r'\[.*\]', '', n)
        n = re.sub(r'\(.*\)', '', n)
        n = re.sub(r'\s+(HD|FHD|SD|4K|ITA|ITALIA|BACKUP|TIMVISION|PLUS)$', '', n)
        
        # Handle Vavoo specific suffixes
        n = re.sub(r'\s+\.[A-Z0-9]{1,3}$', '', n) # Remove " .c", " .s" (Upper because n is upper)
        n = re.sub(r'\s+\+$', '', n)
        n = re.sub(r'[^A-Z0-9 ]', '', n)
        return n.strip()

    def _get_category(self, norm_name):
        for category, keywords in BOUQUETS.items():
            for k in keywords:
                if k in norm_name:
                    return category
        return "Other"

    def _get_priority(self, norm_name):
        # Exact match logic for short names to avoid partial overlap issues
        if norm_name in TIVUSAT_ORDER:
            return TIVUSAT_ORDER[norm_name]
        
        # Substring match if not exact
        for k, v in TIVUSAT_ORDER.items():
            if k in norm_name:
                return v
        return 9999

    def generate_m3u8(self, output_path, groups=None, is_xc=False):
        """
        Generates an M3U8 playlist file with sorting, categorization, and local logos.
        
        Args:
            output_path (str): Path to save the playlist.
            groups (list): Groups to include.
            is_xc (bool): If True, generates XCIPTV/Ottrun compatible format.
        """
        # 1. Delete existing playlist if it exists
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logging.info(f"Deleted existing playlist: {output_path}")
            except OSError as e:
                logging.warning(f"Error deleting existing playlist: {e}")

        channels = self.fetch_all_channels(groups)
        logging.info(f"DEBUG: fetch_all_channels returned {len(channels)} items.")
        
        if not channels:
            logging.warning("No channels found to write.")
            return False

        # Process channels
        processed_channels = []
        logos_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logos") # Assuming script is in python_iptv/src
        
        # Verify logos dir path, fallback to current dir/logos if not found
        if not os.path.exists(logos_dir):
             logos_dir = os.path.join(os.path.dirname(__file__), "logos")

        # Load EPGs to populate names
        logging.info("Loading EPG data for name resolution...")
        self.dm.load_all_epgs()

        for ch in channels:
            norm_name = self._normalize_name(ch['name'])
            
            # BLACKLIST
            if "RAI ITALIA" in norm_name:
                continue
            if "STAR CRIME" in norm_name:
                continue
            if "SKYSHOWTIME 1" in norm_name:
                continue
            if "SKY SPORT FOOTBALL" in norm_name:
                continue
            
            # RENAME
            if norm_name == "RAI":
                # Special case for generic "RAI" which is actually RAI 4K on Vavoo
                norm_name = "RAI 4K"
                ch['final_logo_override'] = "logos/Rai4k.it.png"
                ch['no_epg'] = True
            elif norm_name == "RAI 4K":
                ch['final_logo_override'] = "logos/Rai4k.it.png"
                ch['no_epg'] = True
            elif norm_name == "DISCOVERY NOVE":
                norm_name = "NOVE"
            elif norm_name == "DISCOVERY K2":
                norm_name = "K2"
            elif norm_name == "DISCOVERY FOCUS":
                norm_name = "FOCUS"
            elif norm_name == "MEDIASET IRIS":
                norm_name = "IRIS"
            elif norm_name == "MEDIASET ITALIA 2":
                norm_name = "ITALIA 2"
            elif norm_name == "SKY CINEMA UNO 24":
                norm_name = "SKY CINEMA UNO"
            elif norm_name == "SKY CRIME":
                norm_name = "TOP CRIME"
            elif norm_name == "PREMIUM CRIME":
                norm_name = "TOP CRIME"
            elif norm_name == "SKY SPORT MOTOGP":
                norm_name = "SKY SPORT MOTO GP"
            elif norm_name == "RAI SPORT":
                ch['final_logo_override'] = "logos/rai-sport-hd-it.svg"
            
            category = self._get_category(norm_name)
            priority = self._get_priority(norm_name)
            
            if priority == 9999:
                 if "SKY" in norm_name: priority = 200
                 elif "DAZN" in norm_name: priority = 210
                 elif "PRIMA" in norm_name: priority = 300
            
            # Resolve EPG ID and Logo
            epg_id = "" if ch.get('no_epg') else EPG_MAP.get(norm_name, "")
            
            tvg_id = epg_id if epg_id else norm_name
            if ch.get('no_epg'): tvg_id = ""
            
            tvg_name = tvg_id if tvg_id else ch['name']
            if ch.get('no_epg'):
                tvg_name = ch['name']
                tvg_id = ""
            
            # Resolve Clean Name from EPG
            clean_display_name = norm_name
            if epg_id:
                epg_name = self.dm.get_clean_epg_name(epg_id)
                if epg_name:
                    clean_display_name = epg_name
            
            # Check local logo
            logo_path = ch['logo'] # Default to remote
            if ch.get('final_logo_override'):
                logo_path = ch['final_logo_override'].replace("logos/", "https://github.com/mich-de/vavoo-player/blob/master/logos/") + "?raw=true"
            elif epg_id:
                # Case-insensitive match for local logos (crucial for Linux/GitHub Actions)
                target_fname = f"{epg_id}.png".lower()
                matched_file = None
                
                try:
                    if os.path.exists(logos_dir):
                        for f in os.listdir(logos_dir):
                            if f.lower() == target_fname:
                                matched_file = f
                                break
                except Exception as e:
                    logging.error(f"Error scanning logos directory: {e}")

                if matched_file:
                    logo_path = f"https://github.com/mich-de/vavoo-player/blob/master/logos/{matched_file}?raw=true"
            
            
            
            ch['norm_name'] = norm_name
            ch['group'] = category
            ch['priority'] = priority
            ch['tvg_id'] = tvg_id
            ch['tvg_name'] = tvg_name
            ch['final_logo'] = logo_path
            ch['clean_name'] = clean_display_name
            
            processed_channels.append(ch)

        # Sort
        processed_channels.sort(key=lambda x: (x['priority'], x['group'], x['norm_name']))

        if not processed_channels:
            logging.warning("No valid channels to write.")
            return False

        try:
            logging.info(f"Writing {len(processed_channels)} channels to {output_path} (Format: {'XCIPTV' if is_xc else 'Standard'})...")
            with open(output_path, "w", encoding="utf-8") as f:
                # Include both Primary and Backup EPGs for Italy and Switzerland
                epg_urls = "https://iptv-epg.org/files/epg-it.xml.gz,https://iptv-epg.org/files/epg-ch.xml.gz,https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz,https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz"
                f.write(f'#EXTM3U x-tvg-url="{epg_urls}"\n')
                
                for idx, ch in enumerate(processed_channels, 1):
                    if not is_xc:
                        # Standard Format: include EXTVLCOPT
                        f.write(f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n')
                        header = f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["clean_name"]}" tvg-logo="{ch["final_logo"]}" group-title="{ch["group"]}",{ch["clean_name"]}'
                    else:
                        # XCIPTV Format: UA in header, no EXTVLCOPT, add tvg-chno
                        header = f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["clean_name"]}" tvg-logo="{ch["final_logo"]}" tvg-chno="{idx}" group-title="{ch["group"]}" http-user-agent="{USER_AGENT}",{ch["clean_name"]}'
                    
                    f.write(f"{header}\n")
                    f.write(f"{ch['url']}\n")
                    
            logging.info("Playlist generated successfully.")
            return True
        except Exception as e:
            logging.error(f"Error writing playlist: {e}")
            return False

if __name__ == "__main__":
    # Test run
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("vavoo_player.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    gen = PlaylistGenerator()
    gen.generate_m3u8("test_playlist.m3u8", groups=["Italy", "Switzerland", "Vavoo"])
