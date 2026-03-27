from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPalette

from ui.login_page import LoginPage
from ui.register_page import RegisterPage


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App  —  Sign In")
        self.setMinimumSize(480, 600)
        self.resize(480, 640)

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(9, 11, 20))
        self.setPalette(pal)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._lp = LoginPage(self._show_register)
        self._rp = RegisterPage(self._show_login)
        self.stack.addWidget(self._lp)
        self.stack.addWidget(self._rp)
        self.stack.setCurrentIndex(0)

        # Fade in animation
        self.setWindowOpacity(0.0)
        a = QPropertyAnimation(self, b"windowOpacity")
        a.setDuration(300)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._fade = a

    def _show_register(self):
        self.stack.setCurrentIndex(1)
        self.setWindowTitle("My App  —  Create Account")

    def _show_login(self):
        self.stack.setCurrentIndex(0)
        self.setWindowTitle("My App  —  Sign In")
