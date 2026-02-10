import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Ensure libmpv (in project root) is found
os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ["PATH"]

# --- LOGGING SETUP ---
log_file = os.path.join(os.path.dirname(__file__), "..", "vavoo_player.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import Main Window
from src.ui.main_window import IPTVPlayer

if __name__ == "__main__":
    logging.info("=== Vavoo Player Started ===")
    app = QApplication(sys.argv)
    
    playlist_file = os.path.join(os.path.dirname(__file__), "..", "ITALIA.m3u8")
    if not os.path.exists(playlist_file):
        logging.warning(f"Playlist not found at {playlist_file}, trying local fallback.")
        playlist_file = "ITALIA.m3u8"
        
    player = IPTVPlayer(playlist_file)
    player.show()
    sys.exit(app.exec())
