import os
from queue import PriorityQueue

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem

from .utils import format_time, load_json, save_json


class TagManager(QObject):
    tagAdded = pyqtSignal(QListWidgetItem)

    def __init__(self):
        super().__init__()
        # self.tags = []
        self.tags = PriorityQueue()

    def add_tag(self, tag_time, tag_name, save=True):
        # tag = {"time_ms": tag_time, "tag_name": tag_name}
        # self.tags.append(tag)
        self.tags.put((tag_time, tag_name))
        tag_text = f"[{format_time(tag_time)}] {tag_name}"
        item = QListWidgetItem(tag_text)
        item.setData(Qt.UserRole, (tag_time, tag_name))
        self.tagAdded.emit(item)
        if save:
            self.save_tags_to_json()

    def get_tags(self):
        return self.tags

    def remove_tag(self, tag_time, tag_name, save=True):
        # tag = {"time_ms": tag_time, "tag_name": tag_name}
        # self.tags.remove(tag)
        self.tags.queue.remove((tag_time, tag_name))
        print(f"Removed tag_time: {tag_time}, tag_name: {tag_name}")
        if save:
            self.save_tags_to_json()

    def save_tags_to_json(self, filename="data/tagged_data/tags.json"):
        tags_data = []
        for tag_time, tag_name in self.tags.queue:
            tag = {"time_ms": tag_time, "tag_name": tag_name}
            tags_data.append(tag)
        save_json(tags_data, filename)

    def load_tags_from_json(self, filename="data/tagged_data/tags.json"):
        if not os.path.exists(filename):
            print(f'"{filename}" File not found')
            return

        self.tags.queue.clear()
        tags_data = load_json(filename)

        for tag_info in tags_data:
            time_ms = tag_info["time_ms"]
            tag_name = tag_info["tag_name"]
            self.add_tag(time_ms, tag_name, save=False)

        print(f'Succesfully loaded tags from "{filename}"')
