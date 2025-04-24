import pandas as pd
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem

from .utils import format_time

TAG_TYPE = "CELL_ACTION"


class CellActionTagManager(QObject):
    tagAdded = pyqtSignal(QListWidgetItem)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.tags = []
        self.csv_filename = None
        self.video_start_time = None
        self.cell_action = None

    def add_tag(self, tag):
        self.tags.append(tag)
        time_ms = tag.get("time_ms")
        action_type = tag.get("action_type")
        direction = tag.get("direction")
        if pd.isna(direction):
            direction = ""
        value = tag.get("value")
        level = tag.get("level")
        tag_name = " ".join(filter(lambda a: a != "", [action_type, direction, str(value), level]))
        tag_text = f"[{format_time(time_ms)}] {tag_name}"
        item = QListWidgetItem(tag_text)
        item.setData(Qt.UserRole, tag)
        self.tagAdded.emit(item)

    def set_video_start_time(self, start_time):
        self.video_start_time = start_time

    def load_cell_action(self, csv_filename):
        if csv_filename is None or csv_filename == "":
            csv_filename, _ = QFileDialog.getOpenFileName(
                self.parent,
                "Open Cell Action CSV",
                "",
                "CSV Files (*.csv)",
                options=QFileDialog.DontUseNativeDialog,
            )

        if csv_filename != "":
            self.csv_filename = csv_filename
            self.cell_action = pd.read_csv(
                self.csv_filename, parse_dates=["initial_time", "final_time"]
            )

            print(f"Loading cell action from {self.csv_filename}")

    def load_cell_action_tags(self):
        self.tags = []
        if self.cell_action is not None:
            for _, row in self.cell_action.iterrows():
                if self.video_start_time is None:
                    self.set_video_start_time(row["initial_time"])

                time_ms = int((row["initial_time"] - self.video_start_time).total_seconds() * 1000)
                initial_time = row["initial_time"]
                final_time = row["final_time"]
                action_type = row["type"]
                direction = row["direction"]
                value = row["value"]
                level = row["level"]

                if action_type == "JUM":
                    value = round(value * 100, 1)
                    level = ""
                elif action_type == "DIV":
                    value = ""

                tag = {
                    "time_ms": time_ms,
                    "initial_time": initial_time,
                    "final_time": final_time,
                    "action_type": action_type,
                    "direction": direction,
                    "value": value,
                    "level": level,
                    "tag_type": TAG_TYPE,
                }

                self.add_tag(tag)

    def get_tags(self):
        return self.tags
