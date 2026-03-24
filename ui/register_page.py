from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from services.auth_service import register_user
from ui.ui_components import (
    _Page, _lbl, _inp, PwdField, StatusLabel,
    shake, BTN_PRI, TTL_S, SUB_S, _FF,
    # New imports for enhanced password strength
    check_password_requirements, PasswordRequirementWidget,
    GREEN, RED
)


class RegisterPage(_Page):
    _CARD_H = 620  # Increased height for requirements

    def __init__(self, on_switch):
        super().__init__()
        self._switch = on_switch
        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(0)

        ico = QLabel("")
        ico.setStyleSheet("font-size:20px; color:#6B6CF6; background:transparent; border:none;")
        lay.addWidget(ico)
        lay.addSpacing(14)

        lay.addWidget(QLabel("Create Account", styleSheet=TTL_S))
        sub = QLabel("Fill in your details to get started")
        sub.setStyleSheet(SUB_S + " margin-top:3px;")
        lay.addWidget(sub)
        lay.addSpacing(24)

        # Username
        lay.addWidget(_lbl("USERNAME"))
        lay.addSpacing(7)
        self.u = _inp("Choose a username")
        lay.addWidget(self.u)
        lay.addSpacing(15)

        # Password
        lay.addWidget(_lbl("PASSWORD"))
        lay.addSpacing(7)
        self.p = PwdField("Create a password", height=44)
        self.p.textChanged.connect(self._on_password_changed)
        lay.addWidget(self.p)
        lay.addSpacing(10)

        # Password requirements checklist (from ui_components)
        self.req_widget = PasswordRequirementWidget()
        self.req_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        lay.addWidget(self.req_widget)
        lay.addSpacing(7)

        # Strength bar
        srow = QHBoxLayout()
        srow.setSpacing(8)
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(4)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet("QProgressBar{background:rgba(255,255,255,0.06);border:none;border-radius:2px;} QProgressBar::chunk{border-radius:2px;background:#F87171;}")
        
        self.strength_label = QLabel("")
        self.strength_label.setFixedWidth(44)
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.strength_label.setStyleSheet(f"font-size:11px; color:#F87171; background:transparent; border:none; font-family:{_FF};")
        
        srow.addWidget(self.bar)
        srow.addWidget(self.strength_label)
        lay.addLayout(srow)
        lay.addSpacing(15)

        # Confirm Password
        lay.addWidget(_lbl("CONFIRM PASSWORD"))
        lay.addSpacing(7)
        self.c = PwdField("Re-enter your password", height=44)
        self.c.textChanged.connect(self._check_password_match)
        lay.addWidget(self.c)
        lay.addSpacing(7)

        # Password match indicator
        self.match_label = QLabel("")
        self.match_label.setStyleSheet(f"font-size:11px; color:{RED}; background:transparent; border:none; font-family:{_FF};")
        lay.addWidget(self.match_label)
        lay.addSpacing(5)

        # Status label
        self.st = StatusLabel()
        lay.addSpacing(16)
        lay.addWidget(self.st)
    

        # Create Account button
        self.btn = QPushButton("Create Account")
        self.btn.setFixedHeight(46)
        self.btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn.setStyleSheet(BTN_PRI)
        self.btn.clicked.connect(self._go)
        lay.addWidget(self.btn)
        lay.addSpacing(12)

        # Back button
        bk = QPushButton("← Back to Sign In")
        bk.setFlat(True)
        bk.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bk.setStyleSheet(f"QPushButton{{background:transparent;border:none;color:rgba(195,200,220,0.45);font-size:13px;font-family:{_FF};}} QPushButton:hover{{color:rgba(195,200,220,0.82);}}")
        bk.clicked.connect(self._switch)
        lay.addWidget(bk, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Return key navigation
        self.u.returnPressed.connect(self.p.setFocus)
        self.p.returnPressed.connect(self.c.setFocus)
        self.c.returnPressed.connect(self._go)

        # Initialize with empty password
        self._on_password_changed("")

    def _on_password_changed(self, txt):
        """Handle password changes - update strength and requirements"""
        self._update_password_strength(txt)
        self._check_password_match()

    def _update_password_strength(self, pwd):
        """Update strength meter and requirements checklist"""
        score, strength, color, requirements = check_password_requirements(pwd)
        
        # Update progress bar
        self.bar.setValue(score)
        self.bar.setStyleSheet(f"""
            QProgressBar{{
                background:rgba(255,255,255,0.06);
                border:none;
                border-radius:2px;
            }}
            QProgressBar::chunk{{
                border-radius:2px;
                background:{color};
            }}
        """)
        
        # Update strength label
        self.strength_label.setText(strength)
        self.strength_label.setStyleSheet(f"font-size:11px; color:{color}; background:transparent; border:none; font-family:{_FF};")
        
        # Update requirements checklist
        self.req_widget.update_requirements(requirements)

    def _check_password_match(self):
        """Check if passwords match and update indicator"""
        pwd = self.p.text()
        confirm = self.c.text()
        
        if not pwd or not confirm:
            self.match_label.setText("")
        elif pwd == confirm:
            self.match_label.setText(" Passwords match")
            self.match_label.setStyleSheet(f"font-size:11px; color:{GREEN}; background:transparent; border:none; font-family:{_FF};")
        else:
            self.match_label.setText(" Passwords do not match")
            self.match_label.setStyleSheet(f"font-size:11px; color:{RED}; background:transparent; border:none; font-family:{_FF};")

    def _validate_password(self, pwd):
        """Validate password meets all requirements"""
        _, _, _, requirements = check_password_requirements(pwd)
        return all(requirements.values())

    def _go(self):
        user, pwd, conf = self.u.text().strip(), self.p.text(), self.c.text()
        
        # Check empty fields
        if not user or not pwd or not conf:
            self.st.show_err("Please fill in all fields.")
            shake(self.card)
            return
            
        # Check password match
        if pwd != conf:
            self.st.show_err("Passwords do not match.")
            shake(self.card)
            return
            
        # Validate password strength (all requirements must be met)
        if not self._validate_password(pwd):
            self.st.show_err("Password must be at least 6 characters with uppercase, number, and special character.")
            shake(self.card)
            return
            
        # Proceed with registration
        self.btn.setText("Creating account…")
        self.btn.setEnabled(False)
        self.st.setText("")
        QTimer.singleShot(380, lambda: self._fin(user, pwd))

    def _fin(self, user, pwd):
        ok, msg = register_user(user, pwd)
        self.btn.setText("Create Account")
        self.btn.setEnabled(True)
        if ok:
            self.st.show_ok("  " + msg + " — sign in now.", auto_hide_ms=5000)
            QTimer.singleShot(1600, self._switch)
        else:
            self.st.show_err("  " + msg, auto_hide_ms=8000)
            shake(self.card)