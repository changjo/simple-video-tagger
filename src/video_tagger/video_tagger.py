from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QShortcut,
    QWidget,
)

from .tag_manager import TagManager
from .video_player import VideoPlayer


class VideoTagger(QMainWindow):
    def __init__(self, config):
        super().__init__()

        self.config = config
        window_title = self.config.get("app", {}).get("window_title", "Simple Video Tagger")
        self.setWindowTitle(window_title)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.tag_manager = TagManager()
        self.video_player = VideoPlayer(self.config, self.tag_manager)

        self.tag_list = QListWidget()
        self.tag_list.setFixedWidth(200)
        self.tag_list.setSortingEnabled(True)

        self.tag_manager.tagAdded.connect(self.on_tag_added)
        self.tag_list.itemDoubleClicked.connect(self.on_tag_double_clicked)

        main_layout.addWidget(self.video_player)
        main_layout.addWidget(self.tag_list)

        for tag in self.config["tags"]:
            tag_name = tag["name"]
            key_sequence = tag["shortcut"]
            QShortcut(
                QKeySequence(key_sequence),
                self,
                lambda tag_name=tag_name: self.add_tag(tag_name),
            )

        skip_ms = 2000
        QShortcut(QKeySequence(Qt.Key_Left), self, lambda: self.video_player.skip_time(-skip_ms))
        QShortcut(QKeySequence(Qt.Key_Right), self, lambda: self.video_player.skip_time(skip_ms))

        QShortcut(QKeySequence(Qt.Key_Space), self, self.video_player.toggle_play_pause)

        # ctrl + s 키를 누르면 태그를 저장하는 기능을 추가합니다.
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self, self.tag_manager.save_tags_to_json)

        # self.tag_manager.load_tags_from_json()
        self.tag_manager.load_tags_from_db()
        self.video_player.position_slider.setTags(self.tag_manager.get_tags())
        self.video_player.load_video()

    def add_tag(self, tag_name):
        current_time = self.video_player.player.position()
        self.tag_manager.add_tag(current_time, tag_name)

    def on_tag_added(self, item):
        self.tag_list.addItem(item)
        self.tag_list.scrollToItem(item, QAbstractItemView.PositionAtBottom)
        self.video_player.position_slider.setTags(self.tag_manager.get_tags())

    def on_tag_double_clicked(self, item):
        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.ShiftModifier:
            row = self.tag_list.row(item)
            self.tag_list.takeItem(row)
            time_ms, tag_name = item.data(Qt.UserRole)
            self.tag_manager.remove_tag(time_ms, tag_name)
            self.video_player.position_slider.setTags(self.tag_manager.get_tags())
        else:
            time_ms, tag_name = item.data(Qt.UserRole)  # 저장해둔 밀리초(ms) 시간 꺼내기
            if time_ms is not None:
                self.video_player.player.setPosition(time_ms)
                self.video_player.player.play()
