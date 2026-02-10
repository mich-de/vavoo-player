from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class ChannelItemWidget(QWidget):
    """
    Widget representing a single channel in the list.
    Shows: Logo | Name / Program Title / Progress Bar
    """
    def __init__(self, name, program="", logo_path=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
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
        info_layout.setSpacing(1)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: white; background: transparent;")
        
        self.program_label = QLabel(program)
        self.program_label.setStyleSheet("font-size: 11px; color: #a1a1aa; background: transparent;")
        self.program_label.setWordWrap(False)
        
        # EPG Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("epgProgress")
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()  # Hidden until EPG data is available
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.program_label)
        info_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.logo_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
    def update_program(self, program_title, progress_percent=None):
        """Updates the current program title and progress bar."""
        self.program_label.setText(program_title)
        
        if progress_percent is not None and progress_percent >= 0:
            self.progress_bar.setValue(int(progress_percent))
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
