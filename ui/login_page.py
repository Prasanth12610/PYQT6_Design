from datetime import datetime 

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from services.auth_service import login_user
from ui.ui_components import (
    _Page, _lbl, _inp, PwdField, StatusLabel, _divider,
    shake, BTN_PRI, BTN_GHOST, TTL_S, SUB_S
)


class LoginPage(_Page):
    _CARD_H = 500

    def __init__(self, on_switch):
        super().__init__()
        self._switch = on_switch
        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(0)

        # ── App icon
        ico = QLabel("✦")
        ico.setStyleSheet("font-size:20px; color:#6B6CF6; background:transparent; border:none;")
        lay.addWidget(ico)
        lay.addSpacing(15)

        # ── Title + subtitle
        lay.addWidget(QLabel("Welcome back", styleSheet=TTL_S))
        sub = QLabel("Sign in to your account to continue")
        sub.setStyleSheet(SUB_S + " margin-top:3px;")
        lay.addWidget(sub)
        lay.addSpacing(28)

        # ── Username field
        lay.addWidget(_lbl("USERNAME"))
        lay.addSpacing(7)
        self.u = _inp("Enter your username")
        lay.addWidget(self.u)
        lay.addSpacing(16)

        # ── Password field (with eye-icon toggle)
        lay.addWidget(_lbl("PASSWORD"))
        lay.addSpacing(7)
        self.p = PwdField("Enter your password", height=44)
        lay.addWidget(self.p)
        lay.addSpacing(12)

        # ── Status label (shows success / error messages inline)
        self.st = StatusLabel()
        lay.addWidget(self.st)
        lay.addSpacing(14)

        # ── Sign In button
        self.btn = QPushButton("Sign In")
        self.btn.setFixedHeight(46)
        self.btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn.setStyleSheet(BTN_PRI)
        self.btn.clicked.connect(self._go)
        lay.addWidget(self.btn)
        lay.addSpacing(16)

        # ── Divider + Create Account link
        lay.addLayout(_divider())
        lay.addSpacing(16)

        rb = QPushButton("Create an Account")
        rb.setFixedHeight(43)
        rb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        rb.setStyleSheet(BTN_GHOST)
        rb.clicked.connect(self._switch)
        lay.addWidget(rb)

        # ── Enter key navigation: username → password → submit
        self.u.returnPressed.connect(self.p.setFocus)
        self.p.returnPressed.connect(self._go)

    # =========================================================================
    #  _go()  —  Validate fields then trigger login with a short UI delay
    #  so the button text visibly changes to "Signing in…" before the auth
    #  check runs (makes the UI feel responsive).
    # =========================================================================
    def _go(self):
        user = self.u.text().strip()
        pwd  = self.p.text()

        # Guard: both fields must be filled
        if not user or not pwd:
            self.st.show_err("Please fill in all fields.")
            shake(self.card)
            return

        # Show loading state
        self.btn.setText("Signing in…")
        self.btn.setEnabled(False)
        self.st.setText("")

        # 380 ms delay lets Qt repaint the button before blocking auth call
        QTimer.singleShot(380, lambda: self._fin(user, pwd))

    # =========================================================================
    #  _fin()  —  Receive auth result and act on it
    #  On success: show message → wait 600 ms → open dashboard
    #  On failure: show error + shake animation
    # =========================================================================
    def _fin(self, user, pwd):
        result   = login_user(user, pwd)
        ok       = result[0]
        msg      = result[1]
        entry_id = result[2] if len(result) > 2 else None

        # Re-enable button regardless of outcome
        self.btn.setText("Sign In")
        self.btn.setEnabled(True)

        if ok:
            self.st.show_ok("✓  " + msg + "  — opening dashboard…", auto_hide_ms=2000)

            # Capture login timestamp NOW (datetime is imported at top of file)
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Brief delay so the user sees the success message before switching
            QTimer.singleShot(600, lambda: self._open_dashboard(user, entry_id, login_time))
        else:
            self.st.show_err("✕  " + msg, auto_hide_ms=8000)
            shake(self.card)

    # =========================================================================
    #  _open_dashboard()  —  Switch to DashboardWindow and hide login window
    # =========================================================================
    def _open_dashboard(self, user, entry_id, login_time):
        from ui.dashboard_ui import DashboardWindow

        # Keep a reference so the dashboard isn't garbage-collected
        self._dashboard = DashboardWindow(user, str(entry_id or "0"), login_time)
        self._dashboard.show()

        # Hide the login window (not close — dashboard's Sign Out reopens it)
        self.window().hide()