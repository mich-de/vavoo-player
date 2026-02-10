# --- STYLESHEET ---
# Main application stylesheet in English

STYLESHEET = """
QMainWindow {
    background-color: #0f0f12;
    color: white;
}
QWidget {
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #18181b;
    border-right: 1px solid #27272a;
}
QLabel#appTitle {
    font-size: 18px;
    font-weight: bold;
    color: white;
}
QLineEdit#searchBar {
    background-color: #27272a;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    color: white;
    font-size: 13px;
}

/* Top Bar */
QWidget#topBar {
    background-color: #0f0f12;
    border-bottom: 1px solid #27272a;
}

/* Channel List */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    background-color: transparent;
    border-radius: 6px;
    margin: 2px 4px;
    padding: 0px;
}
QListWidget::item:hover {
    background-color: #27272a;
}
QListWidget::item:selected {
    background-color: #5b13ec;
}

/* Controls */
QWidget#controlsWidget {
    background-color: #18181b; 
    border-top: 1px solid #27272a;
}
QLabel#videoTitle {
    font-size: 16px;
    font-weight: bold;
    color: white;
}
QLabel#videoSubtitle {
    font-size: 12px;
    color: #a1a1aa;
}
QPushButton.controlBtn {
    background: transparent;
    border: none;
    border-radius: 4px;
    color: #e4e4e7;
}
QPushButton.controlBtn:hover {
    background: #27272a;
    color: white;
}

/* EPG Progress Bar */
QProgressBar#epgProgress {
    background-color: #27272a;
    border: none;
    border-radius: 1px;
    max-height: 3px;
}
QProgressBar#epgProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5b13ec, stop:1 #8b5cf6);
    border-radius: 1px;
}
"""
