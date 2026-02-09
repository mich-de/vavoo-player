from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from datetime import datetime, timezone

class ChannelItemWidget(QWidget):
    """
    Widget representing a single channel in the list.
    """
    def __init__(self, name, program="", logo_path=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setStyleSheet("background: #27272a; border-radius: 4px;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_path:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: white; background: transparent;")
        
        self.program_label = QLabel(program)
        self.program_label.setStyleSheet("font-size: 11px; color: #a1a1aa; background: transparent;")
        self.program_label.setWordWrap(False)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #27272a;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #5b13ec;
                border-radius: 2px;
            }
        """)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.program_label)
        info_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.logo_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Store times for refresh
        self.start_dt = None
        self.stop_dt = None
        
    def update_program(self, program_title, start_dt=None, stop_dt=None):
        """Updates the current program title and progress bar."""
        self.program_label.setText(program_title)
        self.start_dt = start_dt
        self.stop_dt = stop_dt
        self._update_progress()
        
    def _update_progress(self):
        """Calculates and updates the progress bar based on current time."""
        if self.start_dt and self.stop_dt:
            now = datetime.now(timezone.utc)
            total = (self.stop_dt - self.start_dt).total_seconds()
            elapsed = (now - self.start_dt).total_seconds()
            if total > 0:
                percent = int(min(100, max(0, (elapsed / total) * 100)))
                self.progress_bar.setValue(percent)
            else:
                self.progress_bar.setValue(0)
        else:
            self.progress_bar.setValue(0)
