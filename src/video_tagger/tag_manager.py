import pandas as pd
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem

from .database import TagDatabase
from .utils import format_time, load_json, save_json


class TagManager(QObject):
    tagAdded = pyqtSignal(QListWidgetItem)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.db_path = None
        self.db = None
        self.video_start_time = None

    def load_db(self, db_path):
        self.db = TagDatabase(db_path)
        self.db_path = db_path

    def add_tag(self, tag):
        tag_time = tag.get("time_ms")
        tag_name = tag.get("tag_name")
        tag_type = tag.get("tag_type")
        tag_text = f"[{format_time(tag_time)}] {tag_name}"
        item = QListWidgetItem(tag_text)
        item.setData(Qt.UserRole, tag)
        self.db.add_tag(tag_time, tag_name, tag_type)
        self.tagAdded.emit(item)

    def get_tags(self):
        tags = self.db.load_tags()
        tags = [
            {
                "time_ms": time_ms,
                "tag_name": tag_name,
                "tag_type": tag_type,
            }
            for time_ms, tag_name, tag_type in tags
        ]
        return tags

        # return self.db.load_tags()
        # return self.tags

    def remove_tag(self, tag_time, tag_name, tag_type):
        # self.tags.remove((tag_time, tag_name))
        print(f"Removed tag_time: {tag_time}, tag_name: {tag_name}, tag_type: {tag_type}")
        self.db.remove_tag(tag_time, tag_name, tag_type)

    def load_tags_from_db(self):
        tags = self.get_tags()
        for tag in tags:
            self.add_tag(tag)
        print(f'Successfully loaded tags from database "{self.db_path}"')

    def set_video_start_time(self, start_time):
        self.video_start_time = start_time

    def save_tags_to_json(self):
        filename = self.db_path.replace(".db", ".json")
        tags = self.db.load_tags()
        columns = ["time_ms", "tag_name", "tag_type"]
        df = pd.DataFrame(tags, columns=columns)
        df.time_ms = pd.to_timedelta(df.time_ms, unit="ms")

        if self.video_start_time is not None:
            df["datetime"] = self.video_start_time + df.time_ms
            df = df[["datetime", "time_ms", "tag_name", "tag_type"]]

        json_data = df.to_dict(orient="records")
        save_json(json_data, filename)
        self.parent.statusBar().showMessage(f'Successfully saved tags to "{filename}"', 5000)
        print(f'Successfully saved tags to "{filename}"')

    def save_tags_to_csv(self):
        filename = self.db_path.replace(".db", ".csv")
        tags = self.db.load_tags()
        columns = ["time_ms", "tag_name", "tag_type"]
        df = pd.DataFrame(tags, columns=columns)
        df.time_ms = pd.to_timedelta(df.time_ms, unit="ms")

        if self.video_start_time is not None:
            df["datetime"] = self.video_start_time + df.time_ms
            df = df[["datetime", "time_ms", "tag_name", "tag_type"]]

        df.to_csv(filename, index=False)
        self.parent.statusBar().showMessage(f'Successfully saved tags to "{filename}"', 5000)
        print(f'Successfully saved tags to "{filename}"')

    def load_tags_from_json(self, filename="data/tagged_data/tags.json"):
        json_data = [
            (tag["time_ms"], tag["tag_name"], tag["tag_type"]) for tag in load_json(filename)
        ]
        for time_ms, tag_name, tag_type in json_data:
            self.add_tag(time_ms, tag_name, tag_type)
        print(f'Successfully loaded tags from "{filename}"')
