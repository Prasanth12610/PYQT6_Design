from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class DevToolsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevTools Inspector")
        self.resize(420, 520)

        layout = QVBoxLayout(self)

        title = QLabel("UI Inspector")
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        layout.addWidget(title)

        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setStyleSheet("font-family: Consolas; font-size:12px;")
        layout.addWidget(self.info)

    def show_widget_info(self, widget):
        parent = widget.parent().__class__.__name__ if widget.parent() else "None"

        style = widget.styleSheet() if hasattr(widget, "styleSheet") else "N/A"

        self.info.setText(f"""
Class: {widget.__class__.__name__}
Object Name: {widget.objectName()}

Parent: {parent}

Size: {widget.size()}
Geometry: {widget.geometry()}

StyleSheet:
{style}
""")
