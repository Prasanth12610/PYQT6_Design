import math
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
    QProgressBar,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QPoint,
    QSize,
    QRectF,
)
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QBrush,
    QPen,
    QCursor,
    QIcon,
    QPixmap,
    QPainterPath,
)


# ------------  Eye icon --------------------
def _eye_icon(visible: bool, px_size=20, color=QColor(150, 155, 185)) -> QIcon:
    sz = px_size
    pm = QPixmap(sz, sz)
    pm.fill(Qt.GlobalColor.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(color)
    pen.setWidthF(1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cx = sz / 2.0
    cy = sz / 2.0
    ew = sz * 0.80
    eh = sz * 0.46

    top = QPainterPath()
    top.moveTo(cx - ew / 2, cy)
    top.cubicTo(cx - ew * 0.28, cy - eh, cx + ew * 0.28, cy - eh, cx + ew / 2, cy)

    bot = QPainterPath()
    bot.moveTo(cx + ew / 2, cy)
    bot.cubicTo(cx + ew * 0.28, cy + eh, cx - ew * 0.28, cy + eh, cx - ew / 2, cy)

    p.drawPath(top)
    p.drawPath(bot)

    if visible:
        pr = sz * 0.175
        p.drawEllipse(QRectF(cx - pr, cy - pr, pr * 2, pr * 2))
    else:
        x1 = cx + ew * 0.38
        y1 = cy - eh * 1.10
        x2 = cx - ew * 0.38
        y2 = cy + eh * 1.10
        p.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))

    p.end()
    return QIcon(pm)


# ----------  Password field widget --------------------

_FF = '"Segoe UI", "SF Pro Text", "Helvetica Neue", sans-serif'


class PwdField(QWidget):
    def __init__(self, placeholder="Password", height=44, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self._vis = False

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._box = QWidget()
        self._box.setFixedHeight(height)
        inner = QHBoxLayout(self._box)
        inner.setContentsMargins(0, 0, 6, 0)
        inner.setSpacing(0)

        self.field = QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.field.setEchoMode(QLineEdit.EchoMode.Password)
        self.field.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                padding: 0px 8px 0px 14px;
                color: #E8EAF0;
                font-size: 14px;
                font-family: {_FF};
            }}
        """)

        self._btn = QPushButton()
        self._btn.setFixedSize(30, 30)
        self._btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn.setFlat(True)
        self._btn.setStyleSheet("QPushButton { background:transparent; border:none; }")
        self._btn.clicked.connect(self._toggle)

        inner.addWidget(self.field)
        inner.addWidget(self._btn)
        outer.addWidget(self._box)

        self._set_border(False)
        self._refresh_icon()
        self.field.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent

        if obj is self.field:
            if event.type() == QEvent.Type.FocusIn:
                self._set_border(True)
            elif event.type() == QEvent.Type.FocusOut:
                self._set_border(False)
        return super().eventFilter(obj, event)

    def _set_border(self, focused: bool):
        if focused:
            b, bg = "rgba(99,179,237,0.75)", "rgba(99,179,237,0.06)"
        else:
            b, bg = "rgba(255,255,255,0.09)", "rgba(255,255,255,0.05)"
        self._box.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 1.5px solid {b};
                border-radius: 9px;
            }}
        """)

    def _toggle(self):
        self._vis = not self._vis
        self.field.setEchoMode(
            QLineEdit.EchoMode.Normal if self._vis else QLineEdit.EchoMode.Password
        )
        self._refresh_icon()

    def _refresh_icon(self):
        col = QColor(195, 200, 225) if self._vis else QColor(140, 145, 175)
        self._btn.setIcon(_eye_icon(self._vis, px_size=20, color=col))
        self._btn.setIconSize(QSize(20, 20))

    def text(self):
        return self.field.text()

    def setFocus(self):
        self.field.setFocus()

    @property
    def returnPressed(self):
        return self.field.returnPressed

    @property
    def textChanged(self):
        return self.field.textChanged


# ----------------  Animated gradient background ---------------


class GradientBG(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(25)

    def _tick(self):
        self._t = (self._t + 1) % 360
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(9, 11, 20))
        cx, cy = self.width() / 2, self.height() / 2
        s = math.sin(math.radians(self._t)) * 70
        g1 = QLinearGradient(cx - 180 + s, cy - 260, cx + 220, cy + 180)
        g1.setColorAt(0, QColor(28, 56, 145, 60))
        g1.setColorAt(1, QColor(9, 11, 20, 0))
        p.setBrush(QBrush(g1))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - 280 + s), int(cy - 300), 560, 520)
        g2 = QLinearGradient(cx + 80 - s * 0.4, cy + 50, cx - 80, cy - 80)
        g2.setColorAt(0, QColor(88, 46, 165, 55))
        g2.setColorAt(1, QColor(9, 11, 20, 0))
        p.setBrush(QBrush(g2))
        p.drawEllipse(int(cx - 60 - s * 0.4), int(cy - 60), 440, 380)


#
#  Glass card
#
class GlassCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(16, 18, 32, 238)))
        p.setPen(QPen(QColor(255, 255, 255, 16), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        p.setPen(QPen(QColor(255, 255, 255, 28), 1))
        p.drawLine(18, 1, self.width() - 18, 1)


#
#  Shake animation
#
def shake(w):
    orig = w.pos()
    a = QPropertyAnimation(w, b"pos")
    a.setDuration(320)
    a.setEasingCurve(QEasingCurve.Type.OutElastic)
    for i, dx in enumerate([10, -10, 7, -7, 4, -4, 0], 1):
        a.setKeyValueAt(i / 7, QPoint(orig.x() + dx, orig.y()))
    a.setEndValue(orig)
    a.start()
    w._shake = a


# ------------  Style constants and helpers -------------------

FIELD_S = f"""
    QLineEdit {{
        background-color: rgba(255,255,255,0.05);
        border: 1.5px solid rgba(255,255,255,0.09);
        border-radius: 9px;
        padding: 0px 14px;
        color: #E8EAF0;
        font-size: 14px;
        font-family: {_FF};
    }}
    QLineEdit:focus {{
        border: 1.5px solid rgba(99,179,237,0.75);
        background-color: rgba(99,179,237,0.06);
        color: #FFFFFF;
    }}
    QLineEdit:hover:!focus {{
        border: 1.5px solid rgba(255,255,255,0.17);
        background-color: rgba(255,255,255,0.07);
    }}
"""

BTN_PRI = f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #4A87F5, stop:1 #7660F0);
        border: none; border-radius: 9px;
        color: #FFFFFF; font-size: 14px; font-weight: 600;
        font-family: {_FF}; letter-spacing: 0.2px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #5A97FF, stop:1 #8670FF);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #3A77E5, stop:1 #6650E0);
    }}
    QPushButton:disabled {{
        background: rgba(90,90,110,0.45);
        color: rgba(255,255,255,0.28);
    }}
"""

BTN_GHOST = f"""
    QPushButton {{
        background: transparent;
        border: 1.5px solid rgba(255,255,255,0.11);
        border-radius: 9px;
        color: rgba(195,200,220,0.72);
        font-size: 13px; font-weight: 500;
        font-family: {_FF};
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,0.055);
        border: 1.5px solid rgba(255,255,255,0.20);
        color: #FFFFFF;
    }}
    QPushButton:pressed {{ background: rgba(255,255,255,0.09); }}
"""

LBL_S = f"font-size:11px; font-weight:600; letter-spacing:1.1px; color:rgba(175,180,205,0.60); background:transparent; border:none; font-family:{_FF};"
TTL_S = f"font-size:24px; font-weight:700; color:#FFFFFF; background:transparent; border:none; letter-spacing:-0.4px; font-family:{_FF};"
SUB_S = f"font-size:13px; color:rgba(195,200,220,0.48); background:transparent; border:none; font-family:{_FF};"
ERR_S = f"font-size:12px; color:#F87171; background:transparent; border:none; font-family:{_FF};"
OK_S = f"font-size:12px; color:#34D399; background:transparent; border:none; font-family:{_FF};"


def _lbl(txt):
    w = QLabel(txt)
    w.setStyleSheet(LBL_S)
    return w


def _inp(ph, h=44):
    w = QLineEdit()
    w.setPlaceholderText(ph)
    w.setFixedHeight(h)
    w.setStyleSheet(FIELD_S)
    return w


def _divider():
    row = QHBoxLayout()
    row.setSpacing(0)
    ln1 = QFrame()
    ln1.setFrameShape(QFrame.Shape.HLine)
    ln1.setStyleSheet("background:rgba(255,255,255,0.07); border:none; max-height:1px;")
    lbl = QLabel("or")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setFixedWidth(32)
    lbl.setStyleSheet(
        f"font-size:12px; color:rgba(195,200,220,0.28); background:transparent; border:none; font-family:{_FF};"
    )
    ln2 = QFrame()
    ln2.setFrameShape(QFrame.Shape.HLine)
    ln2.setStyleSheet("background:rgba(255,255,255,0.07); border:none; max-height:1px;")
    row.addWidget(ln1)
    row.addWidget(lbl)
    row.addWidget(ln2)
    return row


# -----------  Status label with fade-out auto-hide  -----------------


class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(ERR_S)
        self.setText("")
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_fade)

    def show_ok(self, msg, auto_hide_ms=5000):
        self._show(msg, OK_S, auto_hide_ms)

    def show_err(self, msg, auto_hide_ms=8000):
        self._show(msg, ERR_S, auto_hide_ms)

    def _show(self, msg, style, ms):
        self._timer.stop()
        self._cancel_fade()
        self.setStyleSheet(style)
        self.setText(msg)
        if ms > 0:
            self._timer.start(ms)

    def _cancel_fade(self):
        if hasattr(self, "_ft") and self._ft.isActive():
            self._ft.stop()

    def _start_fade(self):
        self._steps = 12
        self._step_i = 0
        self._orig_style = self.styleSheet()
        self._ft = QTimer(self)
        self._ft.timeout.connect(self._step)
        self._ft.start(50)

    def _step(self):
        self._step_i += 1
        alpha = max(0.0, 1.0 - self._step_i / self._steps)
        a = int(alpha * 255)
        r, g, b = (52, 211, 153) if "34D399" in self._orig_style else (248, 113, 113)
        self.setStyleSheet(
            f"font-size:12px; color:rgba({r},{g},{b},{a}); "
            f"background:transparent; border:none; font-family:{_FF};"
        )
        if self._step_i >= self._steps:
            self._ft.stop()
            self.setText("")
            self.setStyleSheet(ERR_S)


# -----------  Password strength helper --------------


def pw_strength(pwd):
    if not pwd:
        return 0, "", "#F87171"
    s = (
        sum(
            [
                len(pwd) >= 6,
                len(pwd) >= 10,
                any(c.isupper() for c in pwd),
                any(c.isdigit() for c in pwd),
                any(c in r"!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd),
            ]
        )
        * 20
    )
    if s <= 20:
        return s, "Weak", "#F87171"
    elif s <= 60:
        return s, "Fair", "#FBBF24"
    else:
        return s, "Strong", "#34D399"


# ---------  Page base ----------------


class _Page(QWidget):
    _CARD_W = 400
    _CARD_H = 500

    def __init__(self):
        super().__init__()
        self.bg = GradientBG(self)
        self.card = GlassCard(self)
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(55)
        sh.setOffset(0, 18)
        sh.setColor(QColor(0, 0, 0, 110))
        self.card.setGraphicsEffect(sh)

    def resizeEvent(self, e):
        self.bg.setGeometry(self.rect())
        W, H = self.width(), self.height()
        cw = min(self._CARD_W, W - 40)
        ch = min(max(self.card.sizeHint().height(), self._CARD_H), H - 40)
        self.card.setGeometry((W - cw) // 2, (H - ch) // 2, cw, ch)


# Color constants for password strength (using existing colors)
GREEN = "#34D399"  # Already defined in OK_S
RED = "#F87171"  # Already defined in ERR_S
YELLOW = "#FBBF24"
BLUE = "#4A87F5"  # From ACCENT in BTN_PRI
TEXT2 = "rgba(195,200,220,0.48)"  # From SUB_S


def check_password_requirements(pwd):
    """
    Enhanced password strength checker
    Returns: (score, strength_text, color, requirements_dict)
    """
    requirements = {
        "length": len(pwd) >= 6,
        "uppercase": any(c.isupper() for c in pwd),
        "number": any(c.isdigit() for c in pwd),
        "special": any(c in r"!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd),
    }

    # Calculate strength score (0-100)
    score = sum(requirements.values()) * 25

    # Determine strength level
    if score <= 25:
        strength = "Weak"
        color = RED
    elif score <= 50:
        strength = "Fair"
        color = YELLOW
    elif score <= 75:
        strength = "Good"
        color = BLUE
    else:
        strength = "Strong"
        color = GREEN

    return score, strength, color, requirements


class PasswordRequirementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 0, 0)
        layout.setSpacing(2)

        self.label = QLabel()
        self.label.setWordWrap(True)

        self.label.setStyleSheet(f"""
            color: {TEXT2};
            font-size: 11px;
            font-family: {_FF};
        """)

        layout.addWidget(self.label)

        # Base text
        self.base_requirements = {
            "length": "At least 6 characters",
            "uppercase": "One uppercase (A-Z)",
            "number": "One number (0-9)",
            "special": "One special (!@#$%)",
        }

        self.update_requirements(
            {"length": False, "uppercase": False, "number": False, "special": False}
        )

    def update_requirements(self, requirements):
        parts = []

        for key, text in self.base_requirements.items():
            if requirements.get(key):
                #  met → green
                parts.append(f"<span style='color:{GREEN};'> {text}</span>")
            else:
                #  not met → dim
                parts.append(f"<span style='color:{TEXT2};'>{text}</span>")

        full_text = " • ".join(parts)

        self.label.setText(
            f"<span style='color:{TEXT2}; font-weight:800;'>Requirements:  </span>"
            f"<span style='line-height:120%;'>[ {full_text} ]</span>"
        )
