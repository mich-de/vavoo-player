import sys
import os
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QListWidget, QListWidgetItem, QLabel, 
                             QLineEdit, QSizePolicy, QStyle, QMessageBox, QStackedLayout)
from PyQt6.QtCore import Qt, QTimer, QSize, QEvent, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

from src.data_manager import DataManager
from src.ui.styles import STYLESHEET
from src.ui.widgets.channel_item import ChannelItemWidget
from src.ui.widgets.controls import ControlsWidget
from src.ui.widgets.loading_overlay import LoadingOverlay
from src.playlist_generator import PlaylistGenerator
from src.ui.player_backend import create_player, get_backend_name, PlayerState

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
        self.top_bar.setFixedHeight(0) # Hidden by default
        
        # --- Video Container with Stacked Layout for Overlay ---
        self.video_container = QWidget()
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_stack = QStackedLayout(self.video_container)
        self.video_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        # Layer 0: Video Frame (MPV render target)
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Enable Mouse Tracking for auto-hide controls
        self.video_frame.setMouseTracking(True)
        self.video_stack.addWidget(self.video_frame)
        
        # Layer 1: Loading Overlay (Transparent background)
        self.overlay_container = QWidget()
        self.overlay_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 
        self.overlay_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay_layout = QVBoxLayout(self.overlay_container)
        self.overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.loading_overlay = LoadingOverlay(self.overlay_container) # Parented to container
        self.loading_overlay.hide() # Initially hidden
        
        self.overlay_layout.addWidget(self.loading_overlay)
        self.video_stack.addWidget(self.overlay_container)
        
        # Controls (Bottom)
        self.controls = ControlsWidget(self)
        
        self.content_layout.addWidget(self.video_container)
        self.content_layout.addWidget(self.controls)
        
        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        # Player Backend Setup
        try:
            self.media_player = create_player()
            backend_name = get_backend_name(self.media_player)
            logging.info(f"Initialized Player Backend: {backend_name}")
            self.setWindowTitle(f"Pro IPTV Player ({backend_name})")
            
            # Connect Signals
            self.media_player.state_changed.connect(self.on_player_state_changed)
            self.media_player.time_changed.connect(self.on_player_time_changed)
            self.media_player.error_occurred.connect(self.on_player_error)
            
        except Exception as e:
            QMessageBox.critical(self, "Player Error", f"Failed to initialize player backend:\n{e}")
            sys.exit(1)
        
        self.all_channels = []
        self.current_channel_index = -1
        self.load_playlist()
        
        self.epg_timer = QTimer()
        self.epg_timer.timeout.connect(self.update_all_epg)
        self.epg_timer.start(60000) # Update titles every minute
        
        # EPG Progress Update Timer
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(30000)
        self.progress_timer.timeout.connect(self.update_epg_progress)
        self.progress_timer.start()
        
        # Fullscreen Auto-Hide Timer
        self.hide_controls_timer = QTimer()
        self.hide_controls_timer.setInterval(3000)
        self.hide_controls_timer.setSingleShot(True)
        self.hide_controls_timer.timeout.connect(self.hide_controls_fullscreen)
        
        # Connection Timeout Timer
        self.connection_timer = QTimer()
        self.connection_timer.setInterval(30000)
        self.connection_timer.setSingleShot(True)
        self.connection_timer.timeout.connect(self.handle_connection_timeout)
        
        # Install event filter
        self.video_frame.installEventFilter(self)
        self.controls.installEventFilter(self)
        
        # Ensure overlay is top
        self.video_stack.setCurrentIndex(1)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def eventFilter(self, source, event):
        if self.is_fullscreen:
            if event.type() == QEvent.Type.MouseMove:
                self.show_controls_fullscreen()
                self.hide_controls_timer.start()
        return super().eventFilter(source, event)
        
    def on_player_state_changed(self, state: PlayerState):
        """Handle state changes from backend."""
        logging.info(f"Player State: {state}")
        
        if state in [PlayerState.OPENING, PlayerState.BUFFERING]:
            self.loading_overlay.show_message("Buffering..." if state == PlayerState.BUFFERING else "Opening...")
            self.loading_overlay.show()
            self.overlay_container.show() # Ensure container is visible
        elif state == PlayerState.PLAYING:
            self.loading_overlay.hide()
            self.overlay_container.hide() 
            self.connection_timer.stop()
            self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        elif state == PlayerState.PAUSED:
            self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        elif state == PlayerState.STOPPED:
            self.controls.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.loading_overlay.hide()
            self.overlay_container.hide()
        elif state == PlayerState.ERROR:
            self.handle_connection_timeout()
        elif state == PlayerState.ENDED:
             pass 

    def on_player_time_changed(self, time_ms):
        """Update time/progress UI if we had a seek bar."""
        pass
        
    def on_player_error(self, error_msg):
        logging.error(f"Player Error: {error_msg}")
        self.loading_overlay.show_message(f"Error: {error_msg}", is_error=True)
        self.overlay_container.show()

    def handle_connection_timeout(self):
        """Called when connection times out."""
        self.media_player.stop()
        self.loading_overlay.show_message("Connection Timeout (30s)", is_error=True)
        self.overlay_container.show()
        self.connection_timer.stop()
        QTimer.singleShot(5000, lambda: [self.loading_overlay.hide(), self.overlay_container.hide()])

    def seek_stream(self, delta_ms):
        """Seeks forward or backward in milliseconds."""
        if self.media_player.is_playing():
            current_time = self.media_player.get_time()
            if current_time != -1:
                new_time = max(0, current_time + delta_ms)
                self.media_player.set_time(new_time)
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
        snap_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "snapshots")
        if not os.path.exists(snap_dir):
            os.makedirs(snap_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_{timestamp}.png"
        path = os.path.abspath(os.path.join(snap_dir, filename))
        
        self.media_player.video_take_snapshot(0, path, 0, 0)
        self.controls.snap_btn.setText("✓")
        QTimer.singleShot(1000, lambda: self.controls.snap_btn.setText(""))
        QTimer.singleShot(1000, lambda: self.controls.snap_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))

    def load_playlist(self):
        if not os.path.exists(self.playlist_path):
            logging.warning(f"Playlist file not found: {self.playlist_path}. Auto-generating...")
            QTimer.singleShot(100, self.refresh_playlist_action)
            return 

        channels, epg_url = self.data_manager.parse_m3u8(self.playlist_path)
        self.all_channels = channels
        self.populate_list(channels)
        
        import threading
        threading.Thread(target=lambda: [self.data_manager.load_all_epgs(), QTimer.singleShot(0, self.update_all_epg)]).start()

    def populate_list(self, channels):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(self.channel_list)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            item.setSizeHint(QSize(0, 60))
            
            local_logo = self.data_manager.find_logo(ch.get('norm_name'))
            # Use local logo if found, otherwise fallback to EPG/M3U8 logo
            logo_to_use = local_logo if local_logo else ch.get('logo')
            
            widget = ChannelItemWidget(ch['name'], "Loading...", logo_to_use)
            self.channel_list.setItemWidget(item, widget)

    def filter_channels(self, text):
        search = text.lower()
        filtered = [ch for ch in self.all_channels if search in ch['name'].lower()]
        self.populate_list(filtered)
        self.update_all_epg()

    def _calculate_progress(self, start_dt, stop_dt):
        if not start_dt or not stop_dt:
            return 0
        now = self.data_manager.get_current_time_cest()
        if start_dt.tzinfo and not now.tzinfo:
            now = now.replace(tzinfo=start_dt.tzinfo)
        if now < start_dt: return 0
        if now > stop_dt: return 100
        total_duration = (stop_dt - start_dt).total_seconds()
        elapsed = (now - start_dt).total_seconds()
        if total_duration <= 0: return 0
        return (elapsed / total_duration) * 100

    def update_all_epg(self):
        logging.info("Starting EPG UI Update for all channels...")
        try:
            for i in range(self.channel_list.count()):
                item = self.channel_list.item(i)
                widget = self.channel_list.itemWidget(item)
                ch = item.data(Qt.ItemDataRole.UserRole)
                if widget and ch:
                    title, _, start_dt, stop_dt = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
                    prog_title = title if title else "No Info Available"
                    
                    # Calculate progress
                    progress = self._calculate_progress(start_dt, stop_dt) if title else None
                    
                    widget.update_program(prog_title, progress)
            logging.info("EPG UI Update finished.")
        except Exception as e:
            import traceback
            logging.error(f"EPG UI Update CRASH: {e}")
            traceback.print_exc()

    def update_epg_progress(self):
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            widget = self.channel_list.itemWidget(item)
            ch = item.data(Qt.ItemDataRole.UserRole)
            if widget and ch:
                _, _, start_dt, stop_dt = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
                if start_dt and stop_dt:
                    progress = self._calculate_progress(start_dt, stop_dt)
                    current_title = widget.program_label.text()
                    widget.update_program(current_title, progress)
            
            # Update Controls Metadata if playing
            if self.current_channel_index == i:
                 title, desc, _, _ = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
                 if title:
                     self.controls.subtitle_label.setText(title)
                     self.controls.desc_label.setText(desc if desc else "")
                     self.controls.desc_label.setToolTip(desc if desc else "")

    def change_channel_offset(self, offset):
        count = self.channel_list.count()
        if count == 0: return
        new_index = (self.current_channel_index + offset) % count
        item = self.channel_list.item(new_index)
        self.channel_list.setCurrentItem(item)
        self.play_channel(item)

    def refresh_playlist_action(self):
        self.loading_overlay.show_message("Updating Playlist...")
        self.overlay_container.show()
        
        self.worker = PlaylistWorker(self.playlist_path)
        self.worker.finished.connect(self.on_playlist_updated)
        self.worker.start()
        
    def on_playlist_updated(self, success, message):
        if success:
            self.load_playlist()
            self.loading_overlay.show_message("Playlist Updated!", is_error=False)
        else:
            self.loading_overlay.show_message("Update Failed!", is_error=True)
        QTimer.singleShot(2000, lambda: [self.loading_overlay.hide(), self.overlay_container.hide()])
        
    def play_channel(self, item):
        self.current_channel_index = self.channel_list.row(item)
        ch = item.data(Qt.ItemDataRole.UserRole)
        logging.info(f"Playing: {ch['url']}")
        
        self.connection_timer.start()
        
        # Stop existing manually to clear state, but play() handles it.
        # However, backend.play will trigger OPENING state which shows overlay
        
        # Embed window
        if sys.platform == "win32":
            # For MPV on Windows with WID, we need to ensure the video_frame has a valid WID
            self.media_player.set_window(int(self.video_frame.winId()))
        elif sys.platform.startswith("linux"):
             self.media_player.set_window(int(self.video_frame.winId()))
        
        # Play
        opts = {
            'user_agent': ch.get('user_agent', 'VAVOO/2.6'),
            'referrer': 'https://vavoo.to/',
            'caching': '5000'
        }
        self.media_player.play(ch['url'], opts)
        
        # Update Info Area
        title, desc, start_dt, stop_dt = self.data_manager.get_current_program(ch.get('id'), ch.get('norm_name'))
        self.controls.title_label.setText(ch['name'])
        self.controls.subtitle_label.setText(title if title else "Live")
        self.controls.desc_label.setText(desc if desc else "")
        self.controls.desc_label.setToolTip(desc if desc else "") # Tooltip for full text if truncated
        
        # Init progress just in case
        if title:
             progress = self._calculate_progress(start_dt, stop_dt)
             widget = self.channel_list.itemWidget(item)
             if widget: widget.update_program(title, progress)
        
        # Update Logo in Controls
        local_logo = self.data_manager.find_logo(ch.get('norm_name'))
        logo_path = local_logo if local_logo else ch.get('logo')
        
        if logo_path:
            pixmap = QPixmap(logo_path)
            # QPixmap(url) fails silently, so for URLs we might need network loading.
            # But at least this enables local files referenced in m3u8/EPG.
            # For URLs, we'd need async loading. For now, this is "better than nothing".
            if not pixmap.isNull():
                self.controls.logo_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                 self.controls.logo_label.clear()
        else:
            self.controls.logo_label.clear()

    def toggle_play(self):
        self.media_player.toggle_pause()

    def set_volume(self, val):
        self.media_player.set_volume(val)

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
