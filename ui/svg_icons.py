# =============================================================================
#  svg_icons.py — SVG Icon Management for Dashboard
#  Contains all SVG icons and icon loading functionality
# =============================================================================

import os
from PyQt6.QtCore import Qt, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Cache for colored icons
_ICON_CACHE = {}


def create_svg_icon(svg_content, size=20, color="#FFFFFF"):
    """Create QIcon from SVG string content with specified color"""
    # Replace currentColor with the specified color
    colored_svg = svg_content.replace(
        'stroke="currentColor"', f'stroke="{color}"')
    colored_svg = colored_svg.replace('fill="currentColor"', f'fill="{color}"')

    # Use colored_svg in the template, NOT svg_content
    svg_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
{colored_svg}
</svg>"""

    # Create pixmap and render SVG to it
    renderer = QSvgRenderer(QByteArray(svg_template.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    if renderer.isValid():
        renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


# Heroicons v2.0 - Outline style (store as strings)
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


def get_icon(name, size=20, color="#FFFFFF"):
    """Get icon by name with specified color"""
    # Create a cache key
    cache_key = f"{name}_{size}_{color}"

    # Return cached icon if available
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    # Create new icon if not in cache
    if name in ICON_SVGS:
        icon = create_svg_icon(ICON_SVGS[name], size, color)
        _ICON_CACHE[cache_key] = icon
        return icon

    print(f"WARNING: Icon '{name}' not found")
    return QIcon()


def clear_icon_cache():
    """Clear the icon cache (useful for debugging)"""
    global _ICON_CACHE
    _ICON_CACHE.clear()
