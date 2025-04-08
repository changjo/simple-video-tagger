from pathlib import Path

from PyQt5.QtCore import QDateTime, QSettings, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDateTimeEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QShortcut,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .cell_action_tag_manager import CellActionTagManager
from .config import load_data_config, save_data_config
from .tag_manager import TagManager
from .utils import load_settings, save_settings
from .video_player import VideoPlayer

MANUAL_TAG_TYPE = "MANUAL"


class VideoTagger(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data_directory = self.open_data_directory()
        if self.data_directory is None:
            return

        self.data_config_path = self.data_directory + "/data_config.yaml"
        self.data_config = load_data_config(self.data_config_path)

        self.config_path = self.data_directory + "/config.yaml"
        self.config = load_settings(self.config_path)

        window_title = self.config.get("app", {}).get("window_title", "Simple Video Tagger")
        self.setWindowTitle(f"{window_title} {__version__}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.setStatusBar(QStatusBar(self))
        self.statusBar().setStyleSheet("QStatusBar { background-color: #2e2e2e; color: white; }")
        self.statusBar().setContentsMargins(0, 0, 0, 0)
        # self.statusBar().setFixedHeight(10)
        self.statusBar().showMessage("Ready", 2000)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.tag_manager = TagManager(self)
        self.video_player = VideoPlayer(self.config, self.tag_manager)

        self.right_layout = QVBoxLayout()
        self.video_start_time_layout = QHBoxLayout()
        self.video_start_time_label = QLabel("Video Start Time (UTC)")
        self.video_start_time_label.setFixedWidth(200)
        self.video_start_time_label.setAlignment(Qt.AlignCenter)
        self.video_start_time_layout.addWidget(self.video_start_time_label)
        self.video_start_time_edit = QDateTimeEdit()
        self.video_start_time_edit.setFixedWidth(200)
        self.video_start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss.zzz")
        self.video_start_time_edit.setDateTime(QDateTime.currentDateTimeUtc())
        self.video_start_time_layout.addWidget(self.video_start_time_edit)
        self.right_layout.addLayout(self.video_start_time_layout)

        self.tag_list_layout = QHBoxLayout()
        self.tag_list = QListWidget()
        self.tag_list.setFixedWidth(200)
        self.tag_list.setSortingEnabled(True)
        self.tag_list_layout.addWidget(self.tag_list)

        self.cell_action_tag_list = QListWidget()  # 새 태그 리스트
        self.cell_action_tag_list.setFixedWidth(200)
        self.cell_action_tag_list.setSortingEnabled(True)
        self.tag_list_layout.addWidget(self.cell_action_tag_list)
        self.right_layout.addLayout(self.tag_list_layout)

        self.tag_manager.tagAdded.connect(self.on_tag_added)
        self.tag_list.itemDoubleClicked.connect(self.on_tag_double_clicked)
        self.cell_action_tag_list.itemDoubleClicked.connect(self.on_cell_action_tag_double_clicked)
        self.video_start_time_edit.dateTimeChanged.connect(self.on_start_time_changed)

        main_layout.addWidget(self.video_player)
        main_layout.addLayout(self.right_layout)

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
        QShortcut(QKeySequence(Qt.Key_Up), self, lambda: self.video_player.increase_play_speed())
        QShortcut(QKeySequence(Qt.Key_Down), self, lambda: self.video_player.decrease_play_speed())

        QShortcut(QKeySequence(Qt.Key_Space), self, self.video_player.toggle_play_pause)

        # ctrl + s 키를 누르면 태그를 저장하는 기능을 추가합니다.
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self, self.tag_manager.save_tags_to_csv)

        self.tag_manager.load_db(self.data_config.db_path)
        self.tag_manager.load_tags_from_db()
        self.video_player.position_slider.setTags(self.tag_manager.get_tags())
        self.video_player.load_video(self.data_config.video_path)
        self.data_config.video_path = self.video_player.video_path

        self.cell_action_tag_manager = CellActionTagManager(self)
        self.cell_action_tag_manager.load_cell_action(self.data_config.imu_action_path)
        self.data_config.imu_action_path = self.cell_action_tag_manager.csv_filename
        self.cell_action_tag_manager.tagAdded.connect(self.on_cell_action_tag_added)
        self.cell_action_tag_manager.load_cell_action_tags()

        if self.cell_action_tag_manager.video_start_time is not None:
            self.video_start_time_edit.setDateTime(self.cell_action_tag_manager.video_start_time)

        self.cell_action_tag_list.setFocus()

        save_settings(self.config, self.config_path)

    def get_recent_data_directory(self):
        settings = QSettings("Fitogether", "SimpleVideoTagger")
        return settings.value("recent_data_directory", "")

    def set_recent_data_directory(self, directory):
        settings = QSettings("Fitogether", "SimpleVideoTagger")
        settings.setValue("recent_data_directory", directory)

    def open_data_directory(self):
        recent_data_directory = self.get_recent_data_directory()

        data_directory = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            recent_data_directory,
            options=QFileDialog.DontUseNativeDialog,
        )
        # if data_directory == "":
        #     data_directory = Path.home() / "video_tagger_data"
        #     data_directory.mkdir(parents=True, exist_ok=True)
        #     data_directory = data_directory.as_posix()
        # else:

        if data_directory == "":
            return None

        self.set_recent_data_directory(data_directory)
        print(f"Selected data directory: {data_directory}")

        return data_directory

    def add_tag(self, tag_name):
        current_time = self.video_player.player.position()
        tag = {"time_ms": current_time, "tag_name": tag_name, "tag_type": MANUAL_TAG_TYPE}
        self.tag_manager.add_tag(tag)

    def on_tag_added(self, item):
        self.tag_list.addItem(item)
        self.tag_list.scrollToItem(item, QAbstractItemView.PositionAtBottom)
        self.video_player.position_slider.setTags(self.tag_manager.get_tags())

    def on_cell_action_tag_added(self, item):
        self.cell_action_tag_list.addItem(item)
        self.video_player.cell_action_position_slider.setTags(
            self.cell_action_tag_manager.get_tags()
        )

    def on_start_time_changed(self, datetime):
        self.cell_action_tag_list.clear()
        self.cell_action_tag_manager.set_video_start_time(datetime.toPyDateTime())
        self.tag_manager.set_video_start_time(datetime.toPyDateTime())
        self.cell_action_tag_manager.load_cell_action_tags()
        self.video_player.cell_action_position_slider.setTags(
            self.cell_action_tag_manager.get_tags()
        )
        self.data_config.video_start_time_utc = datetime.toString("yyyy-MM-dd HH:mm:ss.zzz")
        save_data_config(self.data_config, self.data_config_path)

    def on_tag_double_clicked(self, item):
        modifiers = QApplication.keyboardModifiers()

        tag = item.data(Qt.UserRole)
        time_ms = tag.get("time_ms")
        tag_name = tag.get("tag_name")
        tag_type = tag.get("tag_type")

        if modifiers & Qt.ShiftModifier:
            row = self.tag_list.row(item)
            self.tag_list.takeItem(row)
            self.tag_manager.remove_tag(time_ms, tag_name, tag_type)
            self.video_player.position_slider.setTags(self.tag_manager.get_tags())
        else:
            if time_ms is not None:
                self.video_player.player.setPosition(time_ms)
                self.video_player.player.play()

    def on_cell_action_tag_double_clicked(self, item):
        tag = item.data(Qt.UserRole)
        time_ms = tag.get("time_ms")
        if time_ms is not None:
            self.video_player.player.setPosition(time_ms)
            self.video_player.player.play()
