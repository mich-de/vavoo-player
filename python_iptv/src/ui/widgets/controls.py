from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider, QStyle)
from PyQt6.QtCore import Qt, QTimer

class ControlsWidget(QWidget):
    """
    Widget containing the player controls (Play/Pause, Seek, Volume, etc.)
    """
    def __init__(self, parent_player):
        super().__init__()
        self.parent_player = parent_player
        self.setObjectName("controlsWidget")
        self.setFixedHeight(90)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        
        # --- LEFT: Sidebar Toggle + Logo + Info ---
        self.menu_btn = QPushButton("≡")
        self.menu_btn.setFixedSize(35, 35)
        self.menu_btn.setStyleSheet("background: transparent; border: 1px solid #3f3f46; border-radius: 4px; color: white; font-size: 18px;")
        self.menu_btn.setToolTip("Toggle Sidebar")
        self.menu_btn.clicked.connect(self.parent_player.toggle_sidebar)
        
        # Refresh Button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(35, 35)
        self.refresh_btn.setStyleSheet("background: transparent; border: 1px solid #3f3f46; border-radius: 4px; color: white; font-size: 18px;")
        self.refresh_btn.setToolTip("Refresh Playlist")
        self.refresh_btn.clicked.connect(self.parent_player.refresh_playlist_action)
        
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(50, 50)
        self.logo_label.setStyleSheet("background: #27272a; border-radius: 6px; border: 1px solid #3f3f46;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(2)
        self.title_label = QLabel("Pro IPTV Player")
        self.title_label.setObjectName("videoTitle")
        self.subtitle_label = QLabel("Select a channel")
        self.subtitle_label.setObjectName("videoSubtitle")
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.subtitle_label)
        
        self.layout.addWidget(self.menu_btn)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.refresh_btn)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.logo_label)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.info_layout)
        
        self.layout.addStretch()
        
        # --- CENTER: Playback Controls (Seek -10s, Prev, Play, Next, Seek +10s) ---
        
        # Seek -10s
        self.seek_back_btn = QPushButton("-10s")
        self.seek_back_btn.setProperty("class", "controlBtn")
        self.seek_back_btn.setFixedSize(40, 35)
        self.seek_back_btn.setStyleSheet("font-size: 10px; font-weight: bold; border: 1px solid #3f3f46; border-radius: 4px;")
        self.seek_back_btn.clicked.connect(lambda: self.parent_player.seek_stream(-10000))
        
        self.prev_btn = QPushButton()
        self.prev_btn.setProperty("class", "controlBtn")
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.prev_btn.setFixedSize(35, 35)
        self.prev_btn.clicked.connect(lambda: self.parent_player.change_channel_offset(-1))
        
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(50, 50)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.setStyleSheet("background: white; border-radius: 25px; border: none;")
        self.play_btn.clicked.connect(self.parent_player.toggle_play)
        
        self.next_btn = QPushButton()
        self.next_btn.setProperty("class", "controlBtn")
        self.next_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.next_btn.setFixedSize(35, 35)
        self.next_btn.clicked.connect(lambda: self.parent_player.change_channel_offset(1))
        
        # Seek +10s
        self.seek_fwd_btn = QPushButton("+10s")
        self.seek_fwd_btn.setProperty("class", "controlBtn")
        self.seek_fwd_btn.setFixedSize(40, 35)
        self.seek_fwd_btn.setStyleSheet("font-size: 10px; font-weight: bold; border: 1px solid #3f3f46; border-radius: 4px;")
        self.seek_fwd_btn.clicked.connect(lambda: self.parent_player.seek_stream(10000))
        
        self.layout.addWidget(self.seek_back_btn)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.prev_btn)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.play_btn)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.next_btn)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.seek_fwd_btn)
        
        self.layout.addStretch()
        
        # --- RIGHT: Extra Tools + Volume + Fullscreen ---
        
        # Aspect Ratio
        self.aspect_btn = QPushButton("16:9")
        self.aspect_btn.setProperty("class", "controlBtn")
        self.aspect_btn.setFixedSize(40, 30)
        self.aspect_btn.setStyleSheet("border: 1px solid #3f3f46; border-radius: 4px; color: #a1a1aa; font-size: 10px; font-weight: bold;")
        self.aspect_btn.clicked.connect(self.parent_player.toggle_aspect_ratio)
        
        # Snapshot
        self.snap_btn = QPushButton()
        self.snap_btn.setProperty("class", "controlBtn")
        self.snap_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.snap_btn.setToolTip("Take Snapshot")
        self.snap_btn.setFixedSize(35, 35)
        self.snap_btn.clicked.connect(self.parent_player.take_snapshot)
        
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.setValue(100)
        self.vol_slider.setStyleSheet("QSlider::groove:horizontal { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; } QSlider::handle:horizontal { background: #5b13ec; width: 10px; height: 10px; margin: -3px 0; border-radius: 5px; } QSlider::sub-page:horizontal { background: #5b13ec; }")
        self.vol_slider.valueChanged.connect(self.parent_player.set_volume)
        
        self.fs_btn = QPushButton()
        self.fs_btn.setFixedSize(35, 35)
        self.fs_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.fs_btn.setStyleSheet("background: transparent; border: none; color: #a1a1aa;")
        self.fs_btn.clicked.connect(self.parent_player.toggle_fullscreen)
        
        self.layout.addWidget(self.aspect_btn)
        self.layout.addWidget(self.snap_btn)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.vol_slider)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.fs_btn)
