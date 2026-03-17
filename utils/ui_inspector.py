from PyQt6.QtCore import QObject, QEvent
from utils.devtools_window import DevToolsWindow
from PyQt6.QtWidgets import QWidget

class UIInspector(QObject):
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.devtools = DevToolsWindow()

    def toggle(self):
        self.enabled = not self.enabled

        print("🛠 Dev Mode:", self.enabled)

        if self.enabled:
            self.devtools.show()
            self.devtools.raise_()
        else:
            self.devtools.hide()

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

        # Ignore DevTools window itself
        if obj == self.devtools:
            return False

        # Highlight only (no selection)
        if event.type() == QEvent.Type.Enter:
            try:
                obj.setStyleSheet(obj.styleSheet() + "outline:1px solid red;")
            except:
                pass

        elif event.type() == QEvent.Type.Leave:
            try:
                obj.setStyleSheet(obj.styleSheet().replace("outline:1px solid red;", ""))
            except:
                pass

        elif event.type() == QEvent.Type.MouseButtonPress:
            print("Clicked:", obj.__class__.__name__)

            # Ignore non-widgets (IMPORTANT FIX)
            if not isinstance(obj, QWidget):
                return False

            #Ignore menus/tooltips
            if obj.metaObject().className() in ["QMenu", "QToolTip"]:
                return False

            self.devtools.show_widget_info(obj)

        return False