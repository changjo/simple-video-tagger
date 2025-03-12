from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class OverlayLabel(QLabel):
    def __init__(self, parent=None, width=220):
        super().__init__(parent)
        self.parent = parent

        self.setStyleSheet(
            """
            color: white;
            background-color: rgba(0, 0, 255, 200);
            border: 1px solid white;
            padding: 5px;
            font-size: 14px;
            """
        )
        self.setAlignment(Qt.AlignLeft)
        self.setFixedWidth(width)

        self.move(parent.width() - width, 0)
        self.hide()

    def show_text(self, text):
        self.setText(text)
        self.move(self.parent.width() - self.width(), 0)
        self.adjustSize()
        self.show()

    def hide_text(self):
        self.hide()
