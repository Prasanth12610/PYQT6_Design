import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt  

from ui.main_window import LoginWindow
from utils.xml_handler import init_xml
from utils.ui_inspector import UIInspector


def main():
    init_xml()

    app = QApplication(sys.argv)

    inspector = UIInspector()
    app.installEventFilter(inspector)

    # Load stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())

    win = LoginWindow()
    win.show()

    # SHORTCUT HANDLER
    def toggle_dev():
        print("Shortcut Pressed")
        inspector.toggle()

    # Ctrl + Shift + I
    shortcut1 = QShortcut(QKeySequence("Ctrl+Shift+I"), app)
    shortcut1.setContext(Qt.ShortcutContext.ApplicationShortcut)
    shortcut1.activated.connect(toggle_dev)

    # F12
    shortcut2 = QShortcut(QKeySequence(Qt.Key.Key_F12), app)
    shortcut2.setContext(Qt.ShortcutContext.ApplicationShortcut)
    shortcut2.activated.connect(toggle_dev)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()