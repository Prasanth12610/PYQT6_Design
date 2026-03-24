# =============================================================================
#  dashboard_ui.py  —  v8  PROFESSIONAL UI WITH SVG ICONS
#  
#  CHANGES:
#  1. Added SVG icons from Heroicons/Tabler icons
#  2. Moved vertical scrollbar to right corner
#  3. Professional icon library integration
#  4. All icons are crisp SVG vectors
# =============================================================================

import math
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QGraphicsDropShadowEffect,
    QSizePolicy, QTreeWidget, QTreeWidgetItem, QApplication, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, QParallelAnimationGroup, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import (
    QColor, QPainter, QLinearGradient, QBrush, QCursor, QPalette, QFont,
    QIcon, QPixmap
)

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

from utils.xml_handler import (
    get_all_users, get_login_stats, get_daily_logins,
    log_logout, read_logs,
)

# 
#  DESIGN TOKENS
# 
BG       = "#07090F"
SIDE_BG  = "#0A0C18"
CARD_BG  = "#0E1120"
CARD_BD  = "rgba(255,255,255,0.07)"
HOVER_BG = "#111427"

TEXT1  = "#EDF0F7"
TEXT2  = "#8B90AA"
TEXT3  = "rgba(139,144,170,0.50)"

ACCENT  = "#4F8EF7"
ACCENT2 = "#7B5FED"
GREEN   = "#2DD4AA"
ORANGE  = "#F97316"
RED     = "#F56565"
YELLOW  = "#F6C343"
TEAL    = "#22D3EE"

CHART_C = ["#4F8EF7","#F56565","#2DD4AA","#F6C343",
           "#F97316","#22D3EE","#A78BFA","#F472B6",
           "#86EFAC","#FCA5A5","#67E8F9","#FDE68A"]

_FF = '"Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial", "sans-serif"'


# 
#  SVG ICON LOADER
#  Creates SVG icons from strings (Heroicons/Tabler style)
#  No external files needed - icons are embedded as strings
# 

def create_svg_icon(svg_content, size=20, color="#FFFFFF"):
    """Create QIcon from SVG string content with specified color"""
    # Replace currentColor with the specified color
    colored_svg = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
    colored_svg = colored_svg.replace('fill="currentColor"', f'fill="{color}"')
    
    # Use colored_svg in the template, NOT svg_content
    svg_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
{colored_svg}
</svg>'''
    
    # Create a temporary byte array from the SVG string
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtSvg import QSvgRenderer
    
    # Create pixmap and render SVG to it
    renderer = QSvgRenderer(QByteArray(svg_template.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    if renderer.isValid():
        renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)


# Heroicons v2.0 - Outline style (store as strings, not QIcon objects)
ICON_SVGS = {
    # Navigation
    "dashboard": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9.55228 21 10 20.5523 10 20V16C10 15.4477 10.4477 15 11 15H13C13.5523 15 14 15.4477 14 16V20C14 20.5523 14.4477 21 15 21M9 21H15"/>',
    
    "users": '<path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M15.75 6C15.75 8.8995 13.3995 11.25 10.5 11.25C7.6005 11.25 5.25 8.8995 5.25 6C5.25 3.1005 7.6005 0.75 10.5 0.75C13.3995 0.75 15.75 3.1005 15.75 6Z"/><path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M18.75 21.25H2.25C2.25 16.6936 5.9436 13 10.5 13C15.0564 13 18.75 16.6936 18.75 21.25Z"/><path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M21.75 11.25C21.75 14.1495 19.3995 16.5 16.5 16.5C15.735 16.5 15.015 16.32 14.37 16.005M19.5 21.25H22.5C22.5 18.4822 20.9175 16.0575 18.5625 14.8725"/>',
    
    "analytics": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 13.125C3 12.5037 3.50368 12 4.125 12H6.375C6.99632 12 7.5 12.5037 7.5 13.125V20.25H3V13.125Z"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 8.625C9.75 8.00368 10.2537 7.5 10.875 7.5H13.125C13.7463 7.5 14.25 8.00368 14.25 8.625V20.25H9.75V8.625Z"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 4.125C16.5 3.50368 17.0037 3 17.625 3H19.875C20.4963 3 21 3.50368 21 4.125V20.25H16.5V4.125Z"/><path stroke="currentColor" stroke-linejoin="round" stroke-width="1.5" d="M3 20.25H21"/>',
    
    # Stat card icons
    "users_stat": '<path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M15.75 6C15.75 8.8995 13.3995 11.25 10.5 11.25C7.6005 11.25 5.25 8.8995 5.25 6C5.25 3.1005 7.6005 0.75 10.5 0.75C13.3995 0.75 15.75 3.1005 15.75 6Z"/><path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M18.75 21.25H2.25C2.25 16.6936 5.9436 13 10.5 13C15.0564 13 18.75 16.6936 18.75 21.25Z"/>',
    
    "logins_stat": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 10.5V6.75C16.5 4.2645 14.4855 2.25 12 2.25C9.5145 2.25 7.5 4.2645 7.5 6.75V10.5"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9V13.5"/>',
    
    "today_stat": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6.75 3V5.25M17.25 3V5.25M3 18.75V7.5C3 6.25725 4.00725 5.25 5.25 5.25H18.75C19.9928 5.25 21 6.25725 21 7.5V18.75M3 18.75C3 19.9928 4.00725 21 5.25 21H18.75C19.9928 21 21 19.9928 21 18.75M3 18.75V11.25C3 10.0073 4.00725 9 5.25 9H18.75C19.9928 9 21 10.0073 21 11.25V18.75"/><circle cx="12" cy="15" r="0.75" fill="currentColor"/><circle cx="7.5" cy="15" r="0.75" fill="currentColor"/><circle cx="16.5" cy="15" r="0.75" fill="currentColor"/>',
    
    "session_stat": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6V12L15 15M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3C16.971 3 21 7.029 21 12Z"/>',
    
    # Action icons
    "logout": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 9V5.25C15.75 4.00725 14.7428 3 13.5 3H7.5C6.25725 3 5.25 4.00725 5.25 5.25V18.75C5.25 19.9928 6.25725 21 7.5 21H13.5C14.7428 21 15.75 19.9928 15.75 18.75V15M12 12H21M21 12L18 9M21 12L18 15"/>',
    
    "refresh": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/>',
    
    # Section icons
    "overview": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9.55228 21 10 20.5523 10 20V16C10 15.4477 10.4477 15 11 15H13C13.5523 15 14 15.4477 14 16V20C14 20.5523 14.4477 21 15 21M9 21H15"/>',
    
    "users_section": '<path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M15.75 6C15.75 8.8995 13.3995 11.25 10.5 11.25C7.6005 11.25 5.25 8.8995 5.25 6C5.25 3.1005 7.6005 0.75 10.5 0.75C13.3995 0.75 15.75 3.1005 15.75 6Z"/><path stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="M18.75 21.25H2.25C2.25 16.6936 5.9436 13 10.5 13C15.0564 13 18.75 16.6936 18.75 21.25Z"/>',
    
    "analytics_section": '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 13.125C3 12.5037 3.50368 12 4.125 12H6.375C6.99632 12 7.5 12.5037 7.5 13.125V20.25H3V13.125Z"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 8.625C9.75 8.00368 10.2537 7.5 10.875 7.5H13.125C13.7463 7.5 14.25 8.00368 14.25 8.625V20.25H9.75V8.625Z"/><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 4.125C16.5 3.50368 17.0037 3 17.625 3H19.875C20.4963 3 21 3.50368 21 4.125V20.25H16.5V4.125Z"/>',
}

# Cache for colored icons - use a simple dict
_ICON_CACHE = {}

def get_icon(name, size=20, color="#FFFFFF"):
    """Get icon by name with specified color"""
    # Create a cache key
    cache_key = f"{name}_{size}_{color}"
    
    # Return cached icon if available
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]
    
    # Create new icon if not in cache
    if name in ICON_SVGS:
        print(f"Creating icon: {name}, color={color}, size={size}")
        icon = create_svg_icon(ICON_SVGS[name], size, color)
        _ICON_CACHE[cache_key] = icon
        return icon
    
    print(f"WARNING: Icon '{name}' not found in ICON_SVGS")
    return QIcon()

def _debug_icons(self):
    """Clear icon cache and force reload"""
    global _ICON_CACHE
    _ICON_CACHE.clear()
    print("Icon cache cleared")
    
    # Force update nav buttons
    for btn in self._nav_btns:
        btn._update_icon()

def _test_icons(self):
    """Test icon generation"""
    print("Testing icon generation...")
    
    # Test white icon
    white_icon = get_icon("dashboard", 20, "#FFFFFF")
    print(f"White icon null? {white_icon.isNull()}")
    
    # Test blue icon
    blue_icon = get_icon("dashboard", 20, ACCENT)
    print(f"Blue icon null? {blue_icon.isNull()}")
    
    # Force update all nav buttons
    for btn in self._nav_btns:
        btn._update_icon()

        
# 
#  PulseDot — breathing online indicator
# 
class PulseDot(QWidget):
    def __init__(self, color=GREEN, size=7, parent=None):
        super().__init__(parent)
        self._c = QColor(color)
        self._a = 255
        self._dir = -4
        self.setFixedSize(size + 4, size + 4)
        self._sz = size
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(30)

    def _tick(self):
        self._a = max(70, min(255, self._a + self._dir))
        if self._a in (70, 255):
            self._dir *= -1
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        glow = QColor(self._c)
        glow.setAlpha(int(self._a * 0.22))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self._sz + 4, self._sz + 4)
        dot = QColor(self._c)
        dot.setAlpha(self._a)
        p.setBrush(QBrush(dot))
        p.drawEllipse(2, 2, self._sz, self._sz)


# 
#  HoverCard — border/shadow hover only
# 
class HoverCard(QFrame):
    def __init__(self, accent=ACCENT, radius=14, parent=None):
        super().__init__(parent)
        self._accent = accent
        r, g, b = self._hex_to_rgb(accent)
        self._ss0 = (f"QFrame{{background:{CARD_BG};border:1px solid {CARD_BD};"
                     f"border-radius:{radius}px;}}")
        self._ss1 = (f"QFrame{{background:{HOVER_BG};"
                     f"border:1px solid rgba({r},{g},{b},0.32);"
                     f"border-radius:{radius}px;}}")
        self.setStyleSheet(self._ss0)
        self._sh = QGraphicsDropShadowEffect(self)
        self._sh.setBlurRadius(16)
        self._sh.setOffset(0, 4)
        self._sh.setColor(QColor(0,0,0,55))
        self.setGraphicsEffect(self._sh)

    def enterEvent(self, e):
        self.setStyleSheet(self._ss1)
        r, g, b = self._hex_to_rgb(self._accent)
        self._sh.setBlurRadius(30)
        self._sh.setColor(QColor(r,g,b,38))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setStyleSheet(self._ss0)
        self._sh.setBlurRadius(16)
        self._sh.setColor(QColor(0,0,0,55))
        super().leaveEvent(e)
    
    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)


# 
#  StatCard — KPI cards with SVG icons
# 
class StatCard(HoverCard):
    def __init__(self, title, value, subtitle="",
                 accent=ACCENT, icon_name="dashboard", parent=None):
        super().__init__(accent, 14, parent)
        self.setFixedHeight(112)
        self._target = 0
        self._cur = 0
        self._ct = QTimer(self)
        self._ct.setInterval(14)
        self._ct.timeout.connect(self._count)
        r, g, b = self._hex_to_rgb(accent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(0)

        # Row 1: icon + value
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        # SVG Icon button (non-clickable)
        icon_btn = QPushButton()
        icon_btn.setIcon(get_icon(icon_name, 22, accent))
        icon_btn.setIconSize(QSize(22, 22))
        icon_btn.setFixedSize(38, 38)
        icon_btn.setEnabled(False)
        icon_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba({r},{g},{b},0.15);
                border:none;
                border-radius:11px;
            }}
            QPushButton:disabled {{
                color:{accent};
            }}
        """)
        row1.addWidget(icon_btn)

        mid = QVBoxLayout()
        mid.setSpacing(1)
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(
            f"font-size:28px;font-weight:800;color:{TEXT1};"
            f"background:transparent;border:none;"
        )
        mid.addWidget(self.val_lbl)
        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"font-size:10px;font-weight:700;letter-spacing:1.0px;color:{TEXT2};"
            f"background:transparent;border:none;"
        )
        mid.addWidget(ttl)
        row1.addLayout(mid)
        row1.addStretch()

        # Trend chip (placeholder)
        chip = QLabel("+12%")
        chip.setFixedSize(42, 22)
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setStyleSheet(
            f"background:rgba({r},{g},{b},0.12);color:{accent};"
            f"font-size:9px;font-weight:700;border-radius:7px;border:none;"
        )
        row1.addWidget(chip, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(row1)

        # Subtitle
        if subtitle:
            lay.addSpacing(6)
            sub = QLabel(subtitle)
            sub.setStyleSheet(
                f"font-size:10px;font-weight:400;color:{TEXT3};"
                f"background:transparent;border:none;"
            )
            lay.addWidget(sub)

        lay.addStretch()

        # Bottom gradient bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {accent},stop:0.55 {ACCENT2},stop:1 transparent);"
            f"border-radius:2px;border:none;"
        )
        lay.addWidget(bar)
    
    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

    def set_value(self, v):
        s = str(v)
        if ":" in s:
            self.val_lbl.setText(s)
            return
        try:
            t = int(s)
            if t != self._target:
                self._target = t
                self._ct.start()
        except Exception:
            self.val_lbl.setText(s)

    def _count(self):
        diff = self._target - self._cur
        if diff == 0:
            self._ct.stop()
            return
        step = max(1, abs(diff) // 5)
        self._cur += step if diff > 0 else -step
        if abs(self._target - self._cur) < step:
            self._cur = self._target
        self.val_lbl.setText(str(self._cur))


# 
#  Chart Classes (Pie, Bar, Line only - No Donut)
# 
_CW, _CH   = 4.0, 2.8
_CARD_H    = 220
_TITLE_TOP = 0.88
_LEGEND_B  = 0.18
_AX_L, _AX_R   = 0.14, 0.97
_PIE_L, _PIE_R = 0.04, 0.96


class _Chart(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(figsize=(_CW, _CH), facecolor=CARD_BG)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def _new_ax(self, title=""):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)
        for sp in ax.spines.values():
            sp.set_edgecolor((1, 1, 1, 0.06))
            sp.set_linewidth(0.5)
        ax.tick_params(colors=TEXT2, labelsize=7.5, length=2, pad=2)
        ax.xaxis.label.set_color(TEXT2)
        ax.yaxis.label.set_color(TEXT2)
        if title:
            ax.set_title(title, color=TEXT1, fontsize=9.5,
                         fontweight="700", pad=5, loc="left")
        return ax

    def _done(self):
        self.draw()


class PieChart(_Chart):
    def __init__(self):
        super().__init__()
        self._draw([])

    def _draw(self, users):
        self.fig.subplots_adjust(left=_PIE_L, right=_PIE_R,
                                 top=_TITLE_TOP, bottom=_LEGEND_B)
        ax = self._new_ax("User Distribution")
        if not users:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    color=TEXT2, transform=ax.transAxes, fontsize=9)
            ax.axis("off")
            self._done()
            return
        labels = [u["username"] for u in users]
        sizes = [max(1, u["total_logins"]) for u in users]
        colors = [CHART_C[i % len(CHART_C)] for i in range(len(users))]
        w, _, autos = ax.pie(
            sizes, labels=None, autopct="%1.0f%%", colors=colors,
            startangle=90, pctdistance=0.68, radius=0.90,
            wedgeprops=dict(width=0.44, edgecolor=CARD_BG, linewidth=1.4)
        )
        for t in autos:
            t.set_color(TEXT1)
            t.set_fontsize(7.5)
        ax.legend(w, labels, loc="lower center",
                  bbox_to_anchor=(0.5, -0.10), ncol=min(4, len(labels)),
                  frameon=False, labelcolor=TEXT2, fontsize=7.5)
        self._done()

    def refresh(self, users):
        self._draw(users)


class BarChart(_Chart):
    def __init__(self):
        super().__init__()
        self._draw({})

    def _draw(self, stats):
        self.fig.subplots_adjust(left=_AX_L, right=_AX_R,
                                 top=_TITLE_TOP, bottom=0.30)
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)
        for sp in ax.spines.values():
            sp.set_edgecolor((1, 1, 1, 0.06))
            sp.set_linewidth(0.5)
        ax.tick_params(colors=TEXT2, labelsize=7.5, length=2, pad=2)
        ax.set_title("Login Frequency", color=TEXT1, fontsize=9.5,
                     fontweight="700", pad=5, loc="left")
        if not stats:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    color=TEXT2, transform=ax.transAxes, fontsize=9)
            ax.axis("off")
            self._done()
            return
        names = list(stats.keys())
        counts = list(stats.values())
        colors = [CHART_C[i % len(CHART_C)] for i in range(len(names))]
        bars = ax.bar(names, counts, color=colors, width=0.44,
                      zorder=3, edgecolor="none")
        for b, c in zip(bars, counts):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.04,
                    str(c), ha="center", va="bottom",
                    color=TEXT1, fontsize=8, fontweight="700")
        ax.set_ylabel("Logins", color=TEXT2, fontsize=7.5)
        ax.set_ylim(0, max(counts) * 1.40 + 1)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=5))
        ax.grid(axis="y", color=(1, 1, 1, 0.05), linewidth=0.5, zorder=0)
        import matplotlib.pyplot as _plt
        _plt.setp(ax.get_xticklabels(), rotation=22, ha="right",
                  fontsize=7.5, color=TEXT2)
        self._done()

    def refresh(self, stats):
        self.fig.clear()
        self._draw(stats)


class LineChart(_Chart):
    def __init__(self):
        super().__init__()
        self._draw({})

    def _draw(self, daily):
        self.fig.subplots_adjust(left=_AX_L, right=_AX_R,
                                 top=_TITLE_TOP, bottom=0.26)
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)
        for sp in ax.spines.values():
            sp.set_edgecolor((1, 1, 1, 0.06))
            sp.set_linewidth(0.5)
        ax.tick_params(colors=TEXT2, labelsize=7.5, length=2, pad=2)
        ax.set_title("Daily Trend", color=TEXT1, fontsize=9.5,
                     fontweight="700", pad=5, loc="left")
        if not daily:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    color=TEXT2, transform=ax.transAxes, fontsize=9)
            ax.axis("off")
            self._done()
            return
        dates = sorted(daily.keys())
        counts = [daily[d] for d in dates]
        short = [d[5:] for d in dates]
        ax.plot(short, counts, color=TEAL, linewidth=2.0, marker="o",
                markersize=5, markerfacecolor=ORANGE,
                markeredgewidth=0, zorder=3)
        ax.fill_between(short, counts, alpha=0.08, color=TEAL)
        ax.set_ylabel("Logins", color=TEXT2, fontsize=7.5)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=5))
        ax.grid(color=(1, 1, 1, 0.05), linewidth=0.5)
        import matplotlib.pyplot as _plt
        _plt.setp(ax.get_xticklabels(), rotation=26, ha="right",
                  fontsize=7, color=TEXT2)
        self._done()

    def refresh(self, daily):
        self.fig.clear()
        self._draw(daily)


# 
#  Chart card wrapper
# 
def _chart_card(canvas, accent=ACCENT):
    card = HoverCard(accent, 14)
    card.setFixedHeight(_CARD_H)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(12, 12, 12, 12)
    lay.setSpacing(0)
    lay.addWidget(canvas)
    return card


# 
#  Divider
# 
def _divider():
    d = QFrame()
    d.setFrameShape(QFrame.Shape.HLine)
    d.setFixedHeight(1)
    d.setStyleSheet("background:rgba(255,255,255,0.06);border:none;max-height:1px;")
    return d


# 
#  Section header with SVG icon - IMPROVED STYLING
# 
def _section_hdr(text, chip_text="", chip_color=ACCENT, icon_name=None):
    row = QHBoxLayout()
    row.setSpacing(10)
    row.setContentsMargins(0, 0, 0, 0)
    
    if icon_name:
        icon_btn = QPushButton()
        icon_btn.setIcon(get_icon(icon_name, 20, ACCENT))
        icon_btn.setIconSize(QSize(20, 20))
        icon_btn.setFixedSize(32, 32)
        icon_btn.setEnabled(False)
        r, g, b = HoverCard._hex_to_rgb(ACCENT)
        icon_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba({r},{g},{b},0.12);
                border:none;
                border-radius:8px;
            }}
            QPushButton:disabled {{
                color:{ACCENT};
            }}
        """)
        row.addWidget(icon_btn)
    
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:15px;font-weight:700;color:{TEXT1};"
        f"background:transparent;border:none;letter-spacing:0.3px;"
    )
    row.addWidget(lbl)
    
    if chip_text:
        r, g, b = HoverCard._hex_to_rgb(chip_color)
        chip = QLabel(f"  {chip_text}  ")
        chip.setFixedHeight(24)
        chip.setStyleSheet(
            f"background:rgba({r},{g},{b},0.15);color:{chip_color};"
            f"font-size:10px;font-weight:700;border-radius:8px;border:none;"
            f"padding:0 8px;"
        )
        row.addWidget(chip, 0, Qt.AlignmentFlag.AlignVCenter)
    row.addStretch()
    return row


# 
#  User Table with improved scrollbar (right corner) - FIXED HEADER ALIGNMENT
# 
class UserTable(QTableWidget):
    HEADERS = ["#", "Username", "Registered", "Last Login", "Logins"]

    def __init__(self, min_h=200):
        super().__init__()
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setMinimumHeight(min_h)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setFixedHeight(40)  # Increased from 36
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Center align all headers
        header = self.horizontalHeader()
        for i in range(len(self.HEADERS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background:{CARD_BG};
                alternate-background-color:#0B0D1A;
                border:1px solid {CARD_BD};
                border-radius:14px;
                color:{TEXT1};
                font-size:13px;
                font-weight:400;
                outline:none;
                gridline-color:transparent;
            }}
            QTableWidget::item {{
                padding:0 16px;
                border:none;
                border-bottom:1px solid rgba(255,255,255,0.03);
            }}
            QTableWidget::item:selected {{
                background:rgba(79,142,247,0.15);
                color:#fff;
            }}
            QHeaderView::section {{
                background:rgba(255,255,255,0.03);
                color:{TEXT2};
                font-size:12px;  /* Increased from 10px */
                font-weight:700;
                letter-spacing:1.1px;
                padding:0 16px;
                border:none;
                border-bottom:2px solid rgba(79,142,247,0.3);  /* More visible border */
                text-align:center;  /* Center header text */
            }}
            QHeaderView::section:first {{
                border-top-left-radius:14px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius:14px;
            }}
            QScrollBar:vertical {{
                background:rgba(0,0,0,0.3);
                width:10px;
                border-radius:5px;
                margin:2px 2px 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background:rgba(255,255,255,0.2);
                border-radius:5px;
                min-height:40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background:rgba(255,255,255,0.35);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height:0;
                border:none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background:transparent;
            }}
        """)

    def populate(self, users):
        self.setRowCount(0)
        for i, u in enumerate(users):
            self.insertRow(i)
            vals = [str(i+1), u["username"], u["created"],
                    u["last_login"], str(u["total_logins"])]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                # Center align all items
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if j == 0:
                    item.setForeground(QColor(TEXT2))
                elif j == 4:
                    c = u["total_logins"]
                    item.setForeground(QColor(
                        GREEN if c >= 5 else YELLOW if c >= 2 else TEXT2))
                self.setItem(i, j, item)
            self.setRowHeight(i, 44)


# 
#  Analytics Table with improved scrollbar (right corner) - FIXED HEADER ALIGNMENT
# 
class AnalyticsTable(QTableWidget):
    HEADERS = ["#", "Username", "Login Time", "Logout Time", "Duration", "Status"]

    def __init__(self):
        super().__init__()
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setFixedHeight(40)  # Increased from 36
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumHeight(420)
        
        # Center align all headers
        header = self.horizontalHeader()
        for i in range(len(self.HEADERS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            
        self.setStyleSheet(f"""
            QTableWidget {{
                background:{CARD_BG};
                alternate-background-color:#0B0D1A;
                border:1px solid {CARD_BD};
                border-radius:14px;
                color:{TEXT1};
                font-size:13px;
                font-weight:400;
                outline:none;
            }}
            QTableWidget::item {{
                padding:0 16px;
                border:none;
                border-bottom:1px solid rgba(255,255,255,0.03);
            }}
            QTableWidget::item:selected {{
                background:rgba(79,142,247,0.15);
                color:#fff;
            }}
            QHeaderView::section {{
                background:rgba(255,255,255,0.03);
                color:{TEXT2};
                font-size:12px;  /* Increased from 10px */
                font-weight:700;
                letter-spacing:1.1px;
                padding:0 16px;
                border:none;
                border-bottom:2px solid rgba(79,142,247,0.3);  /* More visible border */
                text-align:center;  /* Center header text */
            }}
            QHeaderView::section:first {{
                border-top-left-radius:14px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius:14px;
            }}
            QScrollBar:vertical {{
                background:rgba(0,0,0,0.3);
                width:10px;
                border-radius:5px;
                margin:2px 2px 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background:rgba(255,255,255,0.2);
                border-radius:5px;
                min-height:40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background:rgba(255,255,255,0.35);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height:0;
                border:none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background:transparent;
            }}
        """)

    def populate(self):
        try:
            logs = read_logs()
            entries = list(reversed(logs.findall("login")))
        except Exception:
            entries = []
        self.setRowCount(0)
        for i, e in enumerate(entries):
            self.insertRow(i)

            def _t(tag):
                el = e.find(tag)
                return (el.text or "")[:16] if el is not None and el.text else "—"

            uname = _t("username")
            lt = _t("login_time")
            lo_el = e.find("logout_time")
            lo = (lo_el.text or "")[:16] if lo_el is not None and lo_el.text else None
            dur_el = e.find("duration_min")
            dur = dur_el.text if dur_el is not None and dur_el.text else None
            active = lo is None
            row_data = [str(i+1), uname, lt,
                        lo or "Active", dur or "—",
                        "Live" if active else "Done"]
            for j, v in enumerate(row_data):
                item = QTableWidgetItem(v)
                # Center align all items
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if j == 0:
                    item.setForeground(QColor(TEXT2))
                if j == 3 and active:
                    item.setForeground(QColor(GREEN))
                if j == 4 and dur:
                    try:
                        d = float(dur)
                        item.setForeground(QColor(
                            GREEN if d < 5 else YELLOW if d < 30 else ORANGE))
                    except Exception:
                        pass
                if j == 5:
                    item.setForeground(QColor(GREEN if active else TEXT2))
                self.setItem(i, j, item)
            self.setRowHeight(i, 44)

# 
#  NavButton with SVG icons - FIXED: Proper icon color control
# 
class NavButton(QPushButton):
    def __init__(self, label, icon_name, accent=ACCENT):
        super().__init__()
        self._label = label
        self._icon_name = icon_name
        self._accent = accent
        self.setFixedHeight(44)
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Initialize with white icon
        self._update_icon()

    def _update_icon(self):
        """Update icon based on checked state"""
        on = self.isChecked()
        # When checked, use accent color; when unchecked, use white
        icon_color = self._accent if on else "#FFFFFF"
        print(f"Updating icon {self._label}: color={icon_color}, checked={on}")
        
        icon = get_icon(self._icon_name, 20, icon_color)
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))
        else:
            print(f"WARNING: Icon {self._icon_name} not found")

    def _style(self):
        on = self.isChecked()
        r, g, b = HoverCard._hex_to_rgb(self._accent)
        self.setText(f"  {self._label}")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background:{"rgba("+str(r)+","+str(g)+","+str(b)+",0.11)" if on else "transparent"};
                border:none;
                border-left:3px solid {self._accent if on else "transparent"};
                border-radius:0px;
                color:{self._accent if on else "#FFFFFF"};
                font-size:13px;
                font-weight:{"700" if on else "500"};
                text-align:left;
                padding-left:22px;
            }}
            QPushButton:hover {{
                background:rgba(255,255,255,0.042);
                color:#FFFFFF;
            }}
        """)

    def setChecked(self, v):
        super().setChecked(v)
        self._update_icon()
        self._style()


# 
#  Scrollable page wrapper (FIXED: scrollbar on right corner)
# 
def _wrap_scroll(w):
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    # Style the scrollbar to appear on the right corner
    sa.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollBar:vertical {
            background: rgba(0,0,0,0.3);
            width: 10px;
            border-radius: 5px;
            margin: 2px 2px 2px 0;
        }
        QScrollBar::handle:vertical {
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            min-height: 40px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255,255,255,0.35);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
    """)
    sa.setWidget(w)
    return sa


# 
#  Page Builders
# 
def _build_overview_page(cards, pie, bar, line, table):
    w = QWidget()
    w.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 2, 20, 20)  # Right margin for scrollbar
    lay.setSpacing(0)

    # KPI stat cards row
    cr = QHBoxLayout()
    cr.setSpacing(12)
    for c in cards:
        cr.addWidget(c)
    lay.addLayout(cr)

    # Analytics section
    lay.addSpacing(18)
    lay.addLayout(_section_hdr("Analytics Overview", "Live", GREEN, "overview"))
    lay.addSpacing(8)

    # Chart grid - 3 charts only
    chart_row_w = QWidget()
    chart_row_w.setStyleSheet("background:transparent;")
    chrw = QHBoxLayout(chart_row_w)
    chrw.setContentsMargins(0, 0, 0, 0)
    chrw.setSpacing(12)

    # Add only 3 charts
    for canvas, acc in zip([pie, bar, line], [ACCENT, ORANGE, TEAL]):
        chrw.addWidget(_chart_card(canvas, acc), 1)

    lay.addWidget(chart_row_w)

    # Table section
    lay.addSpacing(18)
    lay.addLayout(_section_hdr("Registered Users",
                               str(max(0, table.rowCount())), ACCENT, "users_section"))
    lay.addSpacing(8)
    lay.addWidget(table)
    lay.addStretch()
    return w


def _build_users_page(table):
    w = QWidget()
    w.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 2, 20, 20)  # Right margin for scrollbar
    lay.setSpacing(20)

    # Simple header without border/card - just a clean container
    hdr = QWidget()  # Changed from HoverCard to simple QWidget
    hdr.setFixedHeight(50)  # Slightly smaller height
    hdr.setStyleSheet("background:transparent;")  # Ensure no background
    
    hl = QHBoxLayout(hdr)
    hl.setContentsMargins(0, 0, 0, 0)  # Remove all margins
    hl.setSpacing(14)
    
    # # SVG icon for header
    # icon_btn = QPushButton()
    # icon_btn.setIcon(get_icon("users_section", 24, ACCENT))
    # icon_btn.setIconSize(QSize(24, 24))
    # icon_btn.setFixedSize(40, 40)
    # icon_btn.setEnabled(False)
    # r, g, b = HoverCard._hex_to_rgb(ACCENT)
    # icon_btn.setStyleSheet(f"""
    #     QPushButton {{
    #         background:rgba({r},{g},{b},0.13);
    #         border:none;
    #         border-radius:12px;
    #     }}
    #     QPushButton:disabled {{
    #         color:{ACCENT};
    #     }}
    # """)
    # hl.addWidget(icon_btn)
    
    # Title with proper formatting - no border, no background
    title_lbl = QLabel()
    title_lbl.setTextFormat(Qt.TextFormat.RichText)
    title_lbl.setText(
        f"<span style='font-size:18px; font-weight:700; color:{TEXT1}'>Registered Users</span>"
        f" <span style='font-size:14px; color:{TEXT2}'>• All accounts in the system</span>"
    )
    title_lbl.setStyleSheet("background:transparent; border:none;")
    hl.addWidget(title_lbl)
    hl.addStretch()
    
    lay.addWidget(hdr)
    
    # Add a subtle separator line instead of a full card
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFixedHeight(1)
    separator.setStyleSheet(f"background:rgba(255,255,255,0.06); border:none; margin:0;")
    lay.addWidget(separator)
    
    # Section header (keeping this as is)
    lay.addLayout(_section_hdr("User Directory", icon_name="users"))
    lay.addSpacing(8)
    lay.addWidget(table)
    
    return w

def _build_analytics_page(atbl):
    w = QWidget()
    w.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 2, 20, 20)  # Right margin for scrollbar
    lay.setSpacing(20)

    # Simple header without border/card
    hdr = QWidget()  # Changed from HoverCard to simple QWidget
    hdr.setFixedHeight(50)  # Match users page height
    hdr.setStyleSheet("background:transparent;")  # Ensure no background
    
    hl = QHBoxLayout(hdr)
    hl.setContentsMargins(0, 0, 0, 0)  # Remove all margins
    hl.setSpacing(14)
    
    # # SVG icon for header
    # icon_btn = QPushButton()
    # icon_btn.setIcon(get_icon("analytics_section", 24, ACCENT2))
    # icon_btn.setIconSize(QSize(24, 24))
    # icon_btn.setFixedSize(40, 40)
    # icon_btn.setEnabled(False)
    # r, g, b = HoverCard._hex_to_rgb(ACCENT2)
    # icon_btn.setStyleSheet(f"""
    #     QPushButton {{
    #         background:rgba({r},{g},{b},0.13);
    #         border:none;
    #         border-radius:12px;
    #     }}
    #     QPushButton:disabled {{
    #         color:{ACCENT2};
    #     }}
    # """)
    # hl.addWidget(icon_btn)
    
    # Title with proper formatting - no border, no background
    title_lbl = QLabel()
    title_lbl.setTextFormat(Qt.TextFormat.RichText)
    title_lbl.setText(
        f"<span style='font-size:18px; font-weight:700; color:{TEXT1}'>Session History</span>"
        f" <span style='font-size:14px; color:{TEXT2}'>• All login sessions — newest first</span>"
    )
    title_lbl.setStyleSheet("background:transparent; border:none;")
    hl.addWidget(title_lbl)
    hl.addStretch()
    
    # Live sessions count pill
    live_count = 0
    for i in range(atbl.rowCount()):
        if atbl.item(i, 5) and atbl.item(i, 5).text() == "Live":
            live_count += 1
    
    if live_count > 0:
        live_pill = QLabel(f"  {live_count} live  ")
        live_pill.setFixedHeight(28)
        r, g, b = HoverCard._hex_to_rgb(GREEN)
        live_pill.setStyleSheet(f"""
            QLabel {{
                background:rgba({r},{g},{b},0.15);
                color:{GREEN};
                font-size:12px;
                font-weight:700;
                border-radius:14px;
                padding:0 12px;
                border:none;
            }}
        """)
        hl.addWidget(live_pill)
    
    lay.addWidget(hdr)
    
    # Add a subtle separator line
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFixedHeight(1)
    separator.setStyleSheet(f"background:rgba(255,255,255,0.06); border:none; margin:0;")
    lay.addWidget(separator)
    
    # Section header
    lay.addLayout(_section_hdr("Login Sessions", "All Time", ACCENT2, "analytics"))
    lay.addSpacing(8)
    lay.addWidget(atbl)
    
    return w


# 
#  DashboardWindow
# 
class DashboardWindow(QMainWindow):
    def __init__(self, username: str, entry_id: str, login_time: str):
        super().__init__()
        self._user = username
        self._entry_id = entry_id
        self._login_time = login_time
        self._elapsed = 0

        self._sess_timer = QTimer(self)
        self._sess_timer.timeout.connect(self._tick_session)
        self._sess_timer.start(1000)

        self.setWindowTitle(f"Dashboard — {username}")
        self.setMinimumSize(1100, 680)
        self.resize(1300, 840)

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(*HoverCard._hex_to_rgb(BG)))
        self.setPalette(pal)

        root = QWidget()
        self.setCentralWidget(root)
        rl = QHBoxLayout(root)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        rl.addWidget(self._build_sidebar())

        # Right content pane
        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 14, 18, 18)  # Reduced right margin for scrollbar
        cl.setSpacing(12)
        cl.addWidget(self._build_topbar())
        cl.addWidget(_divider())

        # Breadcrumb
        self._bc = QLabel("Overview")
        self._bc.setStyleSheet(f"font-size:11px;font-weight:500;color:{TEXT2};")
        cl.addWidget(self._bc)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background:transparent;border:none;")
        cl.addWidget(self._stack, 1)
        rl.addWidget(content, 1)

        self._init_pages()

        self._ref_timer = QTimer(self)
        self._ref_timer.timeout.connect(self._refresh_all)
        self._ref_timer.start(30_000)

        # Window fade-in
        self.setWindowOpacity(0.0)
        a = QPropertyAnimation(self, b"windowOpacity")
        a.setDuration(300)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._fa = a

    def _animate_refresh(self):
        """Animate refresh button with spinning effect"""
        # Get the refresh button (you'll need to store it as an instance variable)
        if not hasattr(self, '_refresh_btn'):
            return
        
        # Disable button during animation
        self._refresh_btn.setEnabled(False)
        
        # Create rotation animation
        self._refresh_anim = QPropertyAnimation(self._refresh_btn, b"rotation")
        self._refresh_anim.setDuration(800)
        self._refresh_anim.setStartValue(0)
        self._refresh_anim.setEndValue(360)
        self._refresh_anim.setLoopCount(1)
        self._refresh_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Create scale animation for pulse effect
        self._scale_anim = QPropertyAnimation(self._refresh_btn, b"scale")
        self._scale_anim.setDuration(400)
        self._scale_anim.setKeyValueAt(0, 1.0)
        self._scale_anim.setKeyValueAt(0.5, 1.2)
        self._scale_anim.setKeyValueAt(1, 1.0)
        
        # Run animations in parallel
        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._refresh_anim)
        self._anim_group.addAnimation(self._scale_anim)
        
        # Re-enable button when animation finishes
        self._anim_group.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        
        # Start animation
        self._anim_group.start()

    #  Init pages 
    def _init_pages(self):
        users = get_all_users()
        stats = get_login_stats()
        daily = get_daily_logins()
        active = len([u for u in users if u["total_logins"] > 0])
        total = len(users)
        tl = sum(stats.values()) if stats else 0

        # KPI cards with SVG icons
        self._sc_u = StatCard("TOTAL USERS", 0, "Registered accounts", ACCENT, "users_stat")
        self._sc_l = StatCard("TOTAL LOGINS", 0, "All time", ACCENT2, "logins_stat")
        self._sc_t = StatCard("LOGINS TODAY", 0, "Since midnight", GREEN, "today_stat")
        self._sc_s = StatCard("YOUR SESSION", "00:00",
                              f"Logged in as {self._user}", ORANGE, "session_stat")

        def _start():
            self._sc_u.set_value(total)
            self._sc_l.set_value(tl)
            self._sc_t.set_value(self._today())

        QTimer.singleShot(180, _start)

        # Charts
        self._pie = PieChart()
        self._pie.refresh(users)
        self._bar = BarChart()
        self._bar.refresh(stats)
        self._line = LineChart()
        self._line.refresh(daily)

        # Tables
        self._tov = UserTable(200)
        self._tov.populate(users)
        self._tusr = UserTable(420)
        self._tusr.populate(users)
        self._tan = AnalyticsTable()
        self._tan.populate()

        p0 = _build_overview_page(
            [self._sc_u, self._sc_l, self._sc_t, self._sc_s],
            self._pie, self._bar, self._line, self._tov)
        p1 = _build_users_page(self._tusr)
        p2 = _build_analytics_page(self._tan)

        for p in [p0, p1, p2]:
            self._stack.addWidget(_wrap_scroll(p))

        self._stack.setCurrentIndex(0)

    #  Sidebar 
    def _build_sidebar(self):
        sb = QFrame()
        sb.setFixedWidth(216)
        sb.setStyleSheet(f"""
            QFrame {{
                background:{SIDE_BG};
                border-right:1px solid rgba(255,255,255,0.055);
            }}
        """)
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(0, 24, 0, 24)
        lay.setSpacing(0)

        # Logo zone
        logo_w = QWidget()
        logo_w.setFixedHeight(56)
        logo_w.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(logo_w)
        ll.setContentsMargins(20, 0, 20, 0)
        ll.setSpacing(10)
        
        # Logo with gradient background
        sq = QLabel("M")
        sq.setFixedSize(32, 32)
        sq.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sq.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {ACCENT},stop:1 {ACCENT2});"
            f"color:#fff;font-size:14px;font-weight:800;"
            f"border-radius:9px;border:none;"
        )
        ll.addWidget(sq)
        app_name = QLabel("MyApp")
        app_name.setStyleSheet(f"font-size:15px;font-weight:800;color:{TEXT1};")
        ll.addWidget(app_name)
        ll.addStretch()
        lay.addWidget(logo_w)

        lay.addSpacing(20)
        menu_lbl = QLabel("M E N U")
        menu_lbl.setStyleSheet(f"font-size:8px;font-weight:700;color:rgba(139,144,170,0.38);")
        menu_lbl.setContentsMargins(22, 0, 0, 0)
        lay.addWidget(menu_lbl)
        lay.addSpacing(6)

        # Nav buttons with SVG icons
        self._nav_btns = []
        for i, (lbl, icon_name, acc) in enumerate([
            ("Overview", "dashboard", ACCENT),
            ("Users", "users", GREEN),
            ("Analytics", "analytics", ACCENT2),
        ]):
            btn = NavButton(lbl, icon_name, acc)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            lay.addWidget(btn)
            self._nav_btns.append(btn)

        lay.addStretch()

        lay.addWidget(_divider())
        lay.addSpacing(16)

        # Footer: session + avatar + signout
        ft = QWidget()
        ft.setStyleSheet("background:transparent;")
        fl = QVBoxLayout(ft)
        fl.setContentsMargins(18, 0, 18, 0)
        fl.setSpacing(10)

        # Session row
        sr = QHBoxLayout()
        sr.setSpacing(6)
        sr.addWidget(PulseDot(GREEN, 7))
        self._sess_lbl = QLabel("Session: 00:00")
        self._sess_lbl.setStyleSheet(f"font-size:11px;color:{TEXT2};")
        sr.addWidget(self._sess_lbl)
        sr.addStretch()
        fl.addLayout(sr)

        # Avatar row
        ar = QHBoxLayout()
        ar.setSpacing(10)
        av = QLabel(self._user[0].upper())
        av.setFixedSize(32, 32)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r, g, b = HoverCard._hex_to_rgb(ACCENT)
        av.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {ACCENT},stop:1 {ACCENT2});"
            f"color:#fff;font-size:13px;font-weight:800;"
            f"border-radius:16px;"
            f"border:2px solid rgba({r},{g},{b},0.30);"
        )
        ar.addWidget(av)
        user_name = QLabel(self._user)
        user_name.setStyleSheet(f"font-size:13px;font-weight:600;color:{TEXT1};")
        ar.addWidget(user_name)
        ar.addStretch()
        fl.addLayout(ar)
        lay.addWidget(ft)

        lay.addSpacing(12)

        # Sign out with SVG icon
        lo = QWidget()
        lo.setStyleSheet("background:transparent;")
        lol = QHBoxLayout(lo)
        lol.setContentsMargins(14, 0, 14, 0)
        
        sout = QPushButton("  Sign Out")
        sout.setIcon(get_icon("logout", 18, RED))
        sout.setIconSize(QSize(18, 18))
        sout.setFixedHeight(38)
        sout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        r, g, b = HoverCard._hex_to_rgb(RED)
        sout.setStyleSheet(f"""
            QPushButton {{
                background:rgba({r},{g},{b},0.09);
                border:1px solid rgba({r},{g},{b},0.20);
                border-radius:9px;color:{RED};
                font-size:13px;font-weight:600;
                text-align:center;
            }}
            QPushButton:hover {{
                background:rgba({r},{g},{b},0.18);
                border-color:rgba({r},{g},{b},0.38);
            }}
        """)
        sout.clicked.connect(self._logout)
        lol.addWidget(sout)
        lay.addWidget(lo)
        return sb
        # After creating nav buttons
        QTimer.singleShot(100, self._test_icons)  # Test after UI is built

    #  Topbar 
    def _build_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(56) 
        bar.setStyleSheet("background:transparent;")
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{TEXT1};")
        row.addWidget(title)
        row.addStretch()

        # Refresh button with SVG icon - STORE AS INSTANCE VARIABLE
        self._refresh_btn = QPushButton()
        self._refresh_btn.setIcon(get_icon("refresh", 20, TEXT2))
        self._refresh_btn.setIconSize(QSize(20, 20))
        self._refresh_btn.setFixedSize(40, 40)
        self._refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(255,255,255,0.03);
                border:1px solid {CARD_BD};
                border-radius:20px;
            }}
            QPushButton:hover {{
                background:rgba(79,142,247,0.15);
                border-color:{ACCENT}40;
            }}
            QPushButton:disabled {{
                opacity:0.6;
            }}
        """)
        self._refresh_btn.clicked.connect(self._refresh_with_animation)
        row.addWidget(self._refresh_btn)
        
        row.addSpacing(12)

        now = datetime.now().strftime("%a, %d %b %Y")
        self._dlbl = QLabel(now)
        self._dlbl.setStyleSheet(f"font-size:11px;font-weight:500;color:{TEXT2};")
        row.addWidget(self._dlbl)

        row.addSpacing(10)
        vsep = QFrame()
        vsep.setFrameShape(QFrame.Shape.VLine)
        vsep.setFixedSize(1, 16)
        vsep.setStyleSheet("background:rgba(255,255,255,0.12);border:none;")
        row.addWidget(vsep, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addSpacing(10)

        self._tlbl = QLabel(datetime.now().strftime("%H:%M"))
        self._tlbl.setStyleSheet(f"font-size:12px;font-weight:700;color:{TEXT1};")
        row.addWidget(self._tlbl)

        ct = QTimer(self)
        ct.timeout.connect(self._tick_clock)
        ct.start(60_000)
        return bar

    def _refresh_with_animation(self):
        """Refresh data with animation feedback"""
        self._animate_refresh()
        # Small delay to show animation before refresh starts
        QTimer.singleShot(200, self._refresh_all)

    #  Tab switch 
    def _switch(self, idx: int):
        LABELS = ["Overview", "Users", "Analytics"]
        for i, b in enumerate(self._nav_btns):
            b.setChecked(i == idx)
        self._bc.setText(LABELS[idx])
        self._stack.setCurrentIndex(idx)
        if idx == 2:
            self._tan.populate()

    #  Helpers 
    def _today(self):
        return get_daily_logins().get(datetime.now().strftime("%Y-%m-%d"), 0)

    def _tick_session(self):
        self._elapsed += 1
        m, s = divmod(self._elapsed, 60)
        h, m = divmod(m, 60)
        txt = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        self._sess_lbl.setText(f"Session: {txt}")
        self._sc_s.val_lbl.setText(txt)

    def _tick_clock(self):
        self._dlbl.setText(datetime.now().strftime("%a, %d %b %Y"))
        self._tlbl.setText(datetime.now().strftime("%H:%M"))

    def _refresh_all(self):
        users = get_all_users()
        stats = get_login_stats()
        daily = get_daily_logins()
        total = len(users)
        tl = sum(stats.values()) if stats else 0
        active = len([u for u in users if u["total_logins"] > 0])

        self._sc_u.set_value(total)
        self._sc_l.set_value(tl)
        self._sc_t.set_value(self._today())
        self._pie.refresh(users)
        self._bar.refresh(stats)
        self._line.refresh(daily)
        self._tov.populate(users)
        self._tusr.populate(users)
        self._tan.populate()
        self._dlbl.setText(datetime.now().strftime("%a, %d %b %Y"))

    def _logout(self):
        self._sess_timer.stop()
        self._ref_timer.stop()
        log_logout(self._entry_id, self._login_time)
        from ui.main_window import LoginWindow
        self._lw = LoginWindow()
        self._lw.resize(480, 640)
        self._lw.showNormal()
        self.close()

    def closeEvent(self, e):
        self._sess_timer.stop()
        self._ref_timer.stop()
        log_logout(self._entry_id, self._login_time)
        e.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F12:
            if not hasattr(self, "devtools"):
                self.devtools = DevTools(self)
            self.devtools.show()
        
class DevTools(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PyQt Developer Tools")
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        self.info = QLabel("Widget Inspector")
        layout.addWidget(self.info)

        # Widget tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Widget", "Class"])
        layout.addWidget(self.tree)

        # Style editor
        self.style_editor = QTextEdit()
        self.style_editor.setPlaceholderText("Edit stylesheet here...")
        layout.addWidget(self.style_editor)

        self.apply_btn = QPushButton("Apply Style")
        layout.addWidget(self.apply_btn)

        self.apply_btn.clicked.connect(self.apply_style)

        self.populate_widgets()

    def populate_widgets(self):
        """Load all widgets into tree"""
        for widget in QApplication.allWidgets():
            item = QTreeWidgetItem([widget.objectName(), widget.__class__.__name__])
            self.tree.addTopLevelItem(item)

    def apply_style(self):
        """Apply stylesheet live"""
        style = self.style_editor.toPlainText()
        QApplication.instance().setStyleSheet(style)