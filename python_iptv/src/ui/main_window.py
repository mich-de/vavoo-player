import sys
import os
import vlc
import re
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QListWidget, QListWidgetItem, QLabel, 
                             QLineEdit, QSizePolicy, QStyle)
from PyQt6.QtCore import Qt, QTimer, QSize, QEvent, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

from src.data_manager import DataManager
from src.ui.styles import STYLESHEET
from src.ui.widgets.channel_item import ChannelItemWidget
from src.ui.widgets.controls import ControlsWidget
from src.ui.widgets.loading_overlay import LoadingOverlay
from src.playlist_generator import PlaylistGenerator

class PlaylistWorker(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        
    def run(self):
        gen = PlaylistGenerator()
        # Fetch Italy group by default as per user context
        success = gen.generate_m3u8(self.output_path, groups=["Italy"])
        msg = "Playlist updated successfully!" if success else "Failed to update playlist."
        self.finished.emit(success, msg)

class IPTVPlayer(QMainWindow):
    """
    Main application window for the IPTV Player.
    """
    def __init__(self, playlist_path):
        super().__init__()
        self.setWindowTitle("Pro IPTV Player")
        self.resize(1280, 720)
        self.is_fullscreen = False
        self.aspect_ratios = [None, "16:9", "4:3", "1:1", "16:10"]
        self.current_aspect_idx = 0
        
        self.setStyleSheet(STYLESHEET)
        self.data_manager = DataManager()
        self.playlist_path = playlist_path
        
        # --- Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar (Left)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(320)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0,0,0,0)
        
        # Sidebar Content
        self.sidebar_content = QWidget()
        self.sidebar_inner = QVBoxLayout(self.sidebar_content)
        self.sidebar_inner.setContentsMargins(12, 12, 12, 12)
        
        header = QHBoxLayout()
        logo = QLabel("IPTV")
        logo.setStyleSheet("background: #5b13ec; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold;")
        title = QLabel("Pro Player")
        title.setObjectName("appTitle")
        header.addWidget(logo)
        header.addWidget(title)
        header.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_channels)
        
        self.channel_list = QListWidget()
        self.channel_list.itemClicked.connect(self.play_channel)
        
        self.sidebar_inner.addLayout(header)
        self.sidebar_inner.addWidget(self.search_bar)
        self.sidebar_inner.addWidget(self.channel_list)
        
        self.sidebar_layout.addWidget(self.sidebar_content)
        
        # 2. Main Content (Right)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(0)
        
        # Top Bar (Toggle always visible here)
        self.top_bar = QWidget()
        self.top_bar.setObjectName("topBar")
        self.top_bar.setFixedHeight(0) # Hidden by default, sidebar toggle moved to bottom controls
        
        # Video Frame (Middle)
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Enable Mouse Tracking for auto-hide controls in fullscreen
        self.video_frame.setMouseTracking(True)
        
        # Loading Overlay
        self.loading_overlay = LoadingOverlay(self.video_frame)
        self.loading_overlay.hide()
        
        # Controls (Bottom)
        self.controls = ControlsWidget(self)
        
        self.content_layout.addWidget(self.video_frame)
        self.content_layout.addWidget(self.controls)
        
        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        # VLC Setup
        vlc_args = [
            '--http-user-agent=VAVOO/2.6',
            '--no-video-title-show',
            '--quiet',
            '--no-xlib',
            '--network-caching=5000'
        ]
        self.vlc_instance = vlc.Instance(*vlc_args)
        self.media_player = self.vlc_instance.media_player_new()
        self.media_player.video_set_mouse_input(False)
        self.media_player.video_set_key_input(False)
        
        self.all_channels = []
        self.current_channel_index = -1
        self.load_playlist()
        
        self.epg_timer = QTimer()
        self.epg_timer.timeout.connect(self.update_all_epg)
        self.epg_timer.start(60000)
        
        # Fullscreen Auto-Hide Timer
        self.hide_controls_timer = QTimer()
        self.hide_controls_timer.setInterval(3000) # 3 seconds
        self.hide_controls_timer.setSingleShot(True)
        self.hide_controls_timer.timeout.connect(self.hide_controls_fullscreen)
        
        # Connection Timeout Timer (30s)
        self.connection_timer = QTimer()
        self.connection_timer.setInterval(30000)
        self.connection_timer.setSingleShot(True)
        self.connection_timer.timeout.connect(self.handle_connection_timeout)
        
        # Buffering Check Timer
        self.buffering_timer = QTimer()
        self.buffering_timer.setInterval(500)
        self.buffering_timer.timeout.connect(self.check_playback_status)
        
        # Install event filter to capture mouse over video
        self.video_frame.installEventFilter(self)
        self.controls.installEventFilter(self)

    def resizeEvent(self, event):
        # Center overlay on resize
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setFixedSize(300, 100)
            self.loading_overlay.move(
                (self.video_frame.width() - 300) // 2,
                (self.video_frame.height() - 100) // 2
            )
        super().resizeEvent(event)

    def eventFilter(self, source, event):
        if self.is_fullscreen:
            if event.type() == QEvent.Type.MouseMove:
                self.show_controls_fullscreen()
                self.hide_controls_timer.start()
        return super().eventFilter(source, event)
        
    def check_playback_status(self):
        """Checks if VLC is playing or stalled."""
        state = self.media_player.get_state()
        
        if state == vlc.State.Playing:
            self.loading_overlay.hide_overlay()
            self.connection_timer.stop()
            self.buffering_timer.stop()
        elif state == vlc.State.Error:
            self.handle_connection_timeout()
        elif state == vlc.State.Ended or state == vlc.State.Stopped:
             pass # Waiting for user input
             
    def handle_connection_timeout(self):
        """Called when connection times out."""
        self.media_player.stop()
        self.loading_overlay.show_message("Connection Timeout (30s)", is_error=True)
        self.connection_timer.stop()
        self.buffering_timer.stop()
        QTimer.singleShot(5000, self.loading_overlay.hide_overlay)

    def seek_stream(self, delta_ms):
        """Seeks forward or backward in milliseconds."""
        if self.media_player.is_playing():
            current_time = self.media_player.get_time()
            if current_time != -1:
                new_time = max(0, current_time + delta_ms)
                self.media_player.set_time(new_time)
                # Show controls briefly to indicate interaction
                if self.is_fullscreen:
                    self.show_controls_fullscreen()
                    self.hide_controls_timer.start()

    def show_controls_fullscreen(self):
        self.controls.show()

    def hide_controls_fullscreen(self):
        if self.is_fullscreen:
            self.controls.hide()
            self.sidebar.hide()

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def toggle_aspect_ratio(self):
        self.current_aspect_idx = (self.current_aspect_idx + 1) % len(self.aspect_ratios)
        ratio = self.aspect_ratios[self.current_aspect_idx]
        self.media_player.video_set_aspect_ratio(ratio)
        self.controls.aspect_btn.setText(ratio if ratio else "Auto")

    def take_snapshot(self):
        # Ensure snapshots directory exists
        snap_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "snapshots")
        if not os.path.exists(snap_dir):
            os.makedirs(snap_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_{timestamp}.png"
        path = os.path.abspath(os.path.join(snap_dir, filename))
        
        self.media_player.video_take_snapshot(0, path, 0, 0)
        logging.info(f"Snapshot saved to: {path}")
        self.controls.snap_btn.setText("✓")
        QTimer.singleShot(1000, lambda: self.controls.snap_btn.setText(""))
        QTimer.singleShot(1000, lambda: self.controls.snap_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))

    def load_playlist(self):
        if not os.path.exists(self.playlist_path):
            logging.warning(f"Playlist file not found: {self.playlist_path}. Auto-generating...")
            # Use QTimer to allow UI to initialize first if called from __init__
            QTimer.singleShot(100, self.refresh_playlist_action)
            return

        channels, epg_url = self.data_manager.parse_m3u8(self.playlist_path)
        self.all_channels = channels
        self.populate_list(channels)
        
        # Load EPGs from configured sources
        def load_epg_worker():
            self.data_manager.load_all_epgs()
            # Trigger UI update on main thread if needed, or just let the timer/user interaction pick it up
            # But populate_list is already done. We want to refresh the view to show correct names/logos if they changed?
            # self.update_all_epg() is called below in original code.
            # But load_all_epgs is synchronous and slow. It should be threaded!
            
        # Moving EPG load to thread to avoid freezing UI
        import threading
        threading.Thread(target=lambda: [self.data_manager.load_all_epgs(), QTimer.singleShot(0, self.update_all_epg)]).start()

    def populate_list(self, channels):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(self.channel_list)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            item.setSizeHint(QSize(0, 60))
            
            logo_path = self.data_manager.find_logo(ch.get('norm_name'))
            widget = ChannelItemWidget(ch['name'], "Loading...", logo_path)
            self.channel_list.setItemWidget(item, widget)

    def filter_channels(self, text):
        search = text.lower()
        filtered = [ch for ch in self.all_channels if search in ch['name'].lower()]
        self.populate_list(filtered)
        self.update_all_epg()

    def update_all_epg(self):
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            widget = self.channel_list.itemWidget(item)
            ch = item.data(Qt.ItemDataRole.UserRole)
            if widget and ch:
                title, _ = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
                widget.update_program(title if title else "No Info Available")

    def change_channel_offset(self, offset):
        count = self.channel_list.count()
        if count == 0: return
        
        new_index = (self.current_channel_index + offset) % count
        item = self.channel_list.item(new_index)
        self.channel_list.setCurrentItem(item)
        self.play_channel(item)

    def refresh_playlist_action(self):
        """Triggered by the Refresh button in Controls."""
        self.loading_overlay.show_message("Updating Playlist...")
        # Center overlay
        self.loading_overlay.move(
            (self.video_frame.width() - 300) // 2,
            (self.video_frame.height() - 100) // 2
        )
        
        # Default to ITALIA.m3u8 if self.playlist_path is not absolute or correct? 
        # Actually self.playlist_path is passed from main.py, so it should be correct.
        # But if we need to force it:
        # self.worker = PlaylistWorker(self.playlist_path)
        pass # context: self.playlist_path is already set to ITALIA.m3u8 from main.py
        
        self.worker = PlaylistWorker(self.playlist_path)
        self.worker.finished.connect(self.on_playlist_updated)
        self.worker.start()
        
    def on_playlist_updated(self, success, message):
        if success:
            self.load_playlist()
            self.loading_overlay.show_message("Playlist Updated!", is_error=False)
        else:
            self.loading_overlay.show_message("Update Failed!", is_error=True)
            
        QTimer.singleShot(2000, self.loading_overlay.hide_overlay)
        
    def play_channel(self, item):
        self.current_channel_index = self.channel_list.row(item)
        ch = item.data(Qt.ItemDataRole.UserRole)
        logging.info(f"Playing: {ch['url']}")
        
        # Reset and Start timers
        self.connection_timer.start()
        self.buffering_timer.start()
        self.loading_overlay.show_message("Buffering...")
        self.loading_overlay.move(
            (self.video_frame.width() - 300) // 2,
            (self.video_frame.height() - 100) // 2
        )
        
        self.media_player.stop()
        
        if sys.platform == "win32":
            self.media_player.set_hwnd(int(self.video_frame.winId()))
        elif sys.platform.startswith("linux"):
             self.media_player.set_xwindow(int(self.video_frame.winId()))
        
        media = self.vlc_instance.media_new(ch['url'])
        media.add_option(f":http-user-agent=VAVOO/2.6")
        media.add_option(":http-referrer=https://vavoo.to/")
        media.add_option(":network-caching=5000")
        media.add_option(":http-reconnect=true")
        self.media_player.set_media(media)
        
        self.media_player.play()
        
        # Update Info Area
        title, _ = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
        self.controls.title_label.setText(ch['name'])
        self.controls.subtitle_label.setText(title if title else "Live")
        self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        
        # Update Logo in Controls
        logo_path = self.data_manager.find_logo(ch.get('norm_name'))
        if logo_path:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self.controls.logo_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.controls.logo_label.clear()

    def toggle_play(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def set_volume(self, val):
        self.media_player.audio_set_volume(val)

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.sidebar.hide()
            self.top_bar.hide()
            self.controls.hide()
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.sidebar.show()
            self.top_bar.show()
            self.controls.show()
            self.is_fullscreen = False
            
    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()
