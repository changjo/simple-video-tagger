from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QSlider, QStyleOptionSlider


class TagSlider(QSlider):
    def __init__(self, config, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.config = config
        self.tags = []  # 태그가 있는 위치(슬라이더 범위 내의 값)
        self.marker_color = QColor("red")  # 마커 색상
        self.marker_width = 1  # 마커 선 굵기
        self.marker_height = 80  # 마커 선 높이(슬라이더 트랙 위/아래로 얼마나 그릴지)

        self.tag_color = {v["name"]: v["color"] for v in self.config.get("tags", [])}

    def setTags(self, tags):
        """
        태그가 있는 위치 리스트를 슬라이더에 설정.
        positions는 self.minimum() ~ self.maximum() 사이 값들의 리스트로 가정
        """
        self.tags = tags
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        pen = QPen(self.marker_color)
        pen.setWidth(self.marker_width)
        painter.setPen(pen)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove_rect = self.style().subControlRect(
            self.style().CC_Slider, opt, self.style().SC_SliderGroove, self
        )

        slider_min = self.minimum()
        slider_max = self.maximum()
        slider_range = slider_max - slider_min

        y_center = groove_rect.center().y()

        for tag in self.tags:
            time_ms = tag.get("time_ms", 0)
            tag_name = tag.get("tag_name", "")
            if tag_name == "":
                action_type = tag.get("action_type", "")
                direction = tag.get("direction", "")
                if not direction:
                    direction = ""

                tag_name = f"{action_type} {direction}".strip()

            # time_ms, tag_name = tag["time_ms"], tag["tag_name"]
            if slider_range == 0:
                continue
            fraction = (time_ms - slider_min) / slider_range
            # fraction = 0.0 -> 그루브의 왼쪽 끝, 1.0 -> 오른쪽 끝

            x = groove_rect.left() + fraction * groove_rect.width()

            # 마커 선 그리기 (x좌표는 계산된 값, y좌표는 가운데를 기준으로)
            top_y = y_center - (self.marker_height / 2)
            bottom_y = y_center + (self.marker_height / 2)

            tag_color = self.tag_color.get(tag_name, "red")
            pen.setColor(QColor(tag_color))
            painter.setPen(pen)
            painter.drawLine(int(x), int(top_y), int(x), int(bottom_y))

        painter.end()
