from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

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
        self.play_speed = 1.0

        self.overlay_label = OverlayLabel(self.video_widget)

        self.button_layout = QHBoxLayout()

        self.time_label = TimeLabel()
        # self.time_label.setFixedHeight(10)

        self.button_layout.addWidget(self.time_label)
        self.button_layout.addStretch(1)

        self.button_play_toggle = QPushButton("▶")
        self.button_play_toggle.clicked.connect(self.toggle_play_pause)
        self.button_layout.addWidget(self.button_play_toggle)

        self.button_layout.addStretch(1)

        self.button_play_direction_toggle = QPushButton(">")
        self.button_play_direction_toggle.setCheckable(True)
        self.button_play_direction_toggle.clicked.connect(self.toggle_play_direction)
        self.button_layout.addWidget(self.button_play_direction_toggle)

        self.button_speed_minus = QPushButton("⏪")
        self.button_speed_minus.clicked.connect(self.decrease_play_speed)
        self.button_layout.addWidget(self.button_speed_minus)

        self.label_play_speed = QLabel(f"{self.play_speed:.1f}x")
        self.label_play_speed.setFixedWidth(50)
        self.label_play_speed.setAlignment(Qt.AlignCenter)
        self.button_layout.addWidget(self.label_play_speed)

        self.button_speed_plus = QPushButton("⏩")
        self.button_speed_plus.clicked.connect(self.increase_play_speed)
        self.button_layout.addWidget(self.button_speed_plus)

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
        # layout.addWidget(self.time_label)
        layout.addLayout(self.button_layout)
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
            self.update_playing_state()

    def increase_play_speed(self):
        self.play_speed += 0.2
        self.play_speed = min(self.play_speed, 5.0)
        self.apply_playback_speed()

    def decrease_play_speed(self):
        self.play_speed -= 0.2
        self.play_speed = max(self.play_speed, 0.2)
        self.apply_playback_speed()

    def apply_playback_speed(self):
        self.player.setPlaybackRate(self.play_speed)

        self.label_play_speed.setText(f"{self.play_speed:.1f}x")
        self.label_play_speed.adjustSize()

    def toggle_play_direction(self):
        if self.button_play_direction_toggle.isChecked():
            self.button_play_direction_toggle.setText("<")
            self.play_speed = -abs(self.play_speed)
        else:
            self.button_play_direction_toggle.setText(">")
            self.play_speed = abs(self.play_speed)
        self.apply_playback_speed()

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

    def update_playing_state(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.button_play_toggle.setText("⏸")
        else:
            self.button_play_toggle.setText("▶")

        self.toggle_play_direction()

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
        self.update_playing_state()

    def update_time_label(self):
        current_ms = self.player.position()
        total_ms = self.player.duration()
        self.time_label.update_time_label(current_ms, total_ms)
