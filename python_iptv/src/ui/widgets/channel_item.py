from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

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
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.program_label)
        
        layout.addWidget(self.logo_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
    def update_program(self, program_title):
        """Updates the current program title displayed in the widget."""
        self.program_label.setText(program_title)
