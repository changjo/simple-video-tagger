from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from .utils import format_time


class TimeLabel(QWidget):
    def __init__(self):
        super().__init__()

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        layout.addWidget(self.time_label)

    def update_time_label(self, position, duration):
        current_str = format_time(position, show_miliseconds=False)
        total_str = format_time(duration, show_miliseconds=False)
        self.time_label.setText(f"{current_str} / {total_str}")
