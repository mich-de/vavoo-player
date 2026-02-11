import os
import sys
import json
import logging
import re
from flask import Flask, request, jsonify, redirect, Response

# Add the root directory to sys.path to allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.data_manager import DataManager

app = Flask(__name__)

# --- CONFIGURATION ---
PORT = 5000
USERNAME = "admin"
PASSWORD = "vavoo"
PLAYLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "playlist.m3u8")

# --- DATA STORAGE ---
dm = DataManager()
channels = []
categories = []

def load_channels():
    global channels, categories
    if not os.path.exists(PLAYLIST_FILE):
        logging.error(f"Playlist file not found: {PLAYLIST_FILE}. Please generate it first.")
        return False
    
    # Use DataManager to parse the local m3u8
    channels_raw, _ = dm.parse_m3u8(PLAYLIST_FILE)
    channels = channels_raw
    
    # Extract unique categories
    cat_set = set()
    for ch in channels:
        cat_set.add(ch.get('group', 'Other'))
    
    categories = []
    for idx, cat_name in enumerate(sorted(list(cat_set)), 1):
        categories.append({
            "category_id": str(idx),
            "category_name": cat_name,
            "parent_id": 0
        })
    
    logging.info(f"Loaded {len(channels)} channels across {len(categories)} categories.")
    return True

@app.route('/player_api.php')
def player_api():
    user = request.args.get('username')
    pw = request.args.get('password')
    action = request.args.get('action')

    # Basic Auth Check
    if user != USERNAME or pw != PASSWORD:
        return jsonify({"user_info": {"auth": 0}})

    # Server Info Mock
    server_info = {
        "url": request.host_url,
        "port": str(PORT),
        "https_port": "443",
        "server_protocol": "http",
        "rtmp_port": "1935",
        "timezone": "Europe/Rome",
        "timestamp_now": 0,
        "time_now": "2024-01-01 00:00:00"
    }

    user_info = {
        "username": user,
        "password": pw,
        "auth": 1,
        "status": "Active",
        "exp_date": "1943962904",
        "is_trial": "0",
        "active_cons": "0",
        "max_connections": "10",
        "revoked": "0",
        "allowed_outputs": ["m3u8", "ts", "rtmp"]
    }

    if not action:
        return jsonify({"user_info": user_info, "server_info": server_info})

    if action == 'get_live_categories':
        return jsonify(categories)

    if action == 'get_live_streams':
        cat_id = request.args.get('category_id')
        streams = []
        
        target_cat_name = None
        if cat_id:
            for cat in categories:
                if cat['category_id'] == cat_id:
                    target_cat_name = cat['category_name']
                    break
        
        for idx, ch in enumerate(channels, 1):
            if target_cat_name and ch.get('group') != target_cat_name:
                continue
                
            streams.append({
                "num": idx,
                "name": ch['name'],
                "stream_type": "live",
                "stream_id": idx,
                "stream_icon": ch.get('logo', ""),
                "epg_channel_id": ch.get('id', ""),
                "added": "1600000000",
                "category_id": next((c['category_id'] for c in categories if c['category_name'] == ch.get('group', 'Other')), "0"),
                "custom_sid": "",
                "tv_archive": 0,
                "direct_source": "",
                "tv_archive_duration": 0,
                "thumbnail": "",
                "rating": "",
                "rating_5_control": 0,
                "is_adult": 0
            })
        return jsonify(streams)

    return jsonify({"error": "Unknown action"})

# Xtream Live Stream Endpoint
@app.route('/live/<user>/<password>/<int:stream_id>.<ext>')
def live_stream(user, password, stream_id, ext):
    if user != USERNAME or password != PASSWORD:
        return "Unauthorized", 401
    
    if 1 <= stream_id <= len(channels):
        target_url = channels[stream_id - 1]['url']
        return redirect(target_url)
    
    return "Not Found", 404

def run_server():
    from waitress import serve
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    if not load_channels():
        print("Error: Could not load playlist.m3u8. Make sure to generate it first.")
        # sys.exit(1) # Don't exit, maybe it will be generated later
        
    print(f"\nXtream API Emulator started!")
    print(f"Server URL: http://localhost:{PORT}")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")
    print("\nUse the local IP of this PC to connect from other devices on the same Wi-Fi.")
    
    serve(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    run_server()
