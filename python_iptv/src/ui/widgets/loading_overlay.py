from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import Qt

class LoadingOverlay(QWidget):
    """
    Overlay widget to show buffering status and messages.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 8px;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.msg_label = QLabel("Buffering...")
        self.msg_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 0) # Indeterminate mode
        self.progress.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: transparent; } QProgressBar::chunk { background-color: #5b13ec; width: 10px; margin: 1px; }")
        
        layout.addWidget(self.msg_label)
        layout.addWidget(self.progress)
        
        self.hide()
        
    def show_message(self, text, is_error=False):
        self.msg_label.setText(text)
        if is_error:
            self.progress.hide()
            self.msg_label.setStyleSheet("color: #ff4d4d; font-size: 16px; font-weight: bold; background: transparent;")
        else:
            self.progress.show()
            self.msg_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        self.show()
        self.raise_()

    def hide_overlay(self):
        self.hide()
