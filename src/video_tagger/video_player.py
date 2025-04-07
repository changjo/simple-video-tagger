from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from .overlay_label import OverlayLabel
from .tag_slider import TagSlider
from .time_label import TimeLabel
from .utils import format_time


class VideoPlayer(QWidget):
    def __init__(self, config, tag_manager):
        super().__init__()

        self.config = config
        self.tag_manager = tag_manager

        # # 키보드 단축키, 재생/일시정지, 태그 추가 로직 등을 여기에 구현할 수 있음.
        # # 예: self.setFocusPolicy(Qt.StrongFocus) 후 keyPressEvent를 override 등.

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.video_path = None
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.setMinimumSize(1280, 720)

        self.overlay_label = OverlayLabel(self.video_widget)

        self.time_label = TimeLabel()
        self.time_label.setFixedHeight(10)

        self.position_slider = TagSlider(config, Qt.Horizontal)
        self.position_slider.setMinimumHeight(80)
        self.position_slider.setRange(0, 0)
        self.position_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                background: #d0d0d0;
                height: 80px;
                border-radius: 0px;
            }
            QSlider::handle:horizontal {
                background: #555;
                width: 4px;
                border-radius: 0px;
                margin: -2px 0; /* 손잡이가 그루브 중앙에 오도록 */
            }
            """
        )

        self.position_slider.sliderMoved.connect(self.seek_position)
        self.position_slider.sliderPressed.connect(self.pressed_seek_position)

        self.cell_action_position_slider = TagSlider(config, Qt.Horizontal)
        self.cell_action_position_slider.setMinimumHeight(80)
        self.cell_action_position_slider.setRange(0, 0)
        self.cell_action_position_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                background: #d0d0d0;
                height: 80px;
                border-radius: 0px;
            }
            QSlider::handle:horizontal {
                background: #555;
                width: 4px;
                border-radius: 0px;
                margin: -2px 0; /* 손잡이가 그루브 중앙에 오도록 */
            }
            """
        )

        self.cell_action_position_slider.sliderMoved.connect(self.seek_position)
        self.cell_action_position_slider.sliderPressed.connect(
            self.pressed_cell_action_seek_position
        )

        layout.addWidget(self.video_widget)
        layout.addWidget(self.time_label)
        layout.addWidget(self.position_slider)
        layout.addWidget(self.cell_action_position_slider)

        self.player.positionChanged.connect(self.update_slider)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_time_label)
        self.player.durationChanged.connect(self.update_time_label)
        self.player.positionChanged.connect(self.update_overlay_label)

    def load_video(self, video_path):
        if video_path == "" or video_path is None:
            video_path = QFileDialog.getOpenFileName(
                self,
                "Open Video File",
                "",
                "Video Files (*.mp4 *.avi *.mkv)",
                options=QFileDialog.DontUseNativeDialog,
            )[0]

        if video_path != "":
            video_url = QUrl.fromLocalFile(video_path)
            self.video_path = video_path
            self.player.setMedia(QMediaContent(video_url))
            self.player.play()

    def pressed_seek_position(self):
        self.seek_position(self.position_slider.value())

    def pressed_cell_action_seek_position(self):
        self.seek_position(self.cell_action_position_slider.value())

    def seek_position(self, position):
        self.player.setPosition(position)

    def update_slider(self, position):
        self.position_slider.setValue(position)
        self.cell_action_position_slider.setValue(position)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)
        self.cell_action_position_slider.setRange(0, duration)

    def update_overlay_label(self, position):
        tags = self.tag_manager.get_tags()

        active_tags = []
        for tag in tags:
            time_ms = tag.get("time_ms", 0)
            tag_name = tag.get("tag_name", "")
            tag_type = tag.get("tag_type", "")
            if tag_name == "":
                tag_name = (tag.get("action_type", "") + " " + tag.get("direction", "")).strip()

            start_ms = time_ms
            end_ms = time_ms + 1000
            if start_ms <= position <= end_ms:
                tag_text = f"[{format_time(time_ms)}] {tag_name} ({tag_type})"
                active_tags.append(tag_text)

        if active_tags:
            self.overlay_label.show_text("\n".join(active_tags))
            # self.overlay_label.setText("\n".join(active_tags))
            # self.overlay_label.adjustSize()
            # self.overlay_label.show()
        else:
            self.overlay_label.hide_text()

    def skip_time(self, ms):
        new_position = self.player.position() + ms
        self.player.setPosition(new_position)

    def skip_5sec_backward(self):
        new_position = self.player.position() - 5000  # 5000 ms = 5초
        self.player.setPosition(new_position)

    def skip_5sec_forward(self):
        new_position = self.player.position() + 5000  # 5000 ms = 5초
        self.player.setPosition(new_position)

    def skip_2sec_backward(self):
        new_position = self.player.position() - 2000  # 5000 ms = 5초
        self.player.setPosition(new_position)

    def skip_2sec_forward(self):
        new_position = self.player.position() + 2000  # 5000 ms = 5초
        self.player.setPosition(new_position)

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def update_time_label(self):
        current_ms = self.player.position()
        total_ms = self.player.duration()
        self.time_label.update_time_label(current_ms, total_ms)
