import math
from bisect import bisect_left
from typing import Optional

import numpy as np
import pandas as pd
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPainter
from PyQt5.QtWidgets import QOpenGLWidget

from .utils import get_video_time_ms, load_fusion_data


class Cell3dCuboid(QOpenGLWidget):
    def __init__(
        self,
        parent,
        fusion_data_filename: str,
        video_start_time_utc: Optional[pd.Timestamp],
    ):
        super(Cell3dCuboid, self).__init__(parent)

        self.fusion_data = load_fusion_data(fusion_data_filename)
        self.datetimes = self.fusion_data["datetime"]
        print(f"Loaded {len(self.datetimes)} data points from {fusion_data_filename}")

        self.video_start_time_utc = None
        self.video_time_ms = None
        self.set_video_start_time_utc(video_start_time_utc)
        self.euler_angles = self.fusion_data[["euler_x", "euler_y", "euler_z"]].to_numpy()

        self.current_time_ms = 0
        self.data_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScene)
        self.timer.start(10)

        # Device parameters
        self.device_height = 1.0
        self.device_width = 0.5
        self.device_depth = 0.2

        # Grid (background plane) parameters
        self.plane_width = 40.0
        self.plane_height = 40.0
        self.grid_step = 1

        # Axis lengths
        self.device_axis_length = 2.0
        self.global_axis_length = 3.0

        # Camera parameters (고정 값 또는 외부에서 설정 가능)
        self.camera_angle_x = -135  # azimuth (degrees)
        self.camera_angle_y = 45  # elevation (degrees)
        self.camera_distance = 20.0
        self.zoom_sensitivy = 1.0

        self.x_angle = 0
        self.y_angle = 0
        self.z_angle = 0

        self.last_mouse_pos = QPoint()
        self.mouse_left_down = False

        # color format: 0xAABBGGRR
        self.face_labels = {
            "front": ("F", 0xFF0000FF),
            "back": ("B", 0xFF00FF00),
            "left": ("L", 0xFFFF0000),
            "right": ("R", 0xFF00FFFF),
            "top": ("U", 0xFFFF00FF),
            "bottom": ("D", 0xFFFFFF00),
        }
        self.textures = {}

    def set_video_start_time_utc(self, video_start_time_utc):
        if video_start_time_utc is pd.NaT:
            video_start_time_utc = self.datetimes[0]

        self.video_start_time_utc = video_start_time_utc
        self.video_time_ms = get_video_time_ms(self.datetimes, self.video_start_time_utc)
        print(f"Updated video start time: {self.video_start_time_utc}")

    def set_current_video_time_ms(self, time_ms):
        self.current_time_ms = time_ms
        self.data_index = bisect_left(self.video_time_ms, time_ms)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_left_down = True
            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_left_down = False

    def mouseMoveEvent(self, event):
        if not self.mouse_left_down:
            return

        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        sensitivity = 0.5

        self.camera_angle_x += dx * sensitivity
        self.camera_angle_y += dy * sensitivity
        self.camera_angle_y = max(-89, min(89, self.camera_angle_y))  # Clamp elevation

        self.last_mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.camera_distance -= delta * self.zoom_sensitivy
        self.camera_distance = max(1.0, min(100.0, self.camera_distance))
        self.update()

    def make_cell_box_texture(self):
        for face, (char, color) in self.face_labels.items():
            img = QImage(128, 128, QImage.Format_RGBA8888)

            img.fill(color)

            # QPainter로 중앙에 글자 그리기
            painter = QPainter(img)
            font = QFont("Helvetica", 128, QFont.Bold)
            painter.setFont(font)
            painter.setPen(Qt.white)
            painter.drawText(img.rect(), Qt.AlignCenter, char)
            painter.end()

            # 바이트 버퍼 얻기
            ptr = img.bits()
            ptr.setsize(img.byteCount())
            data = ptr.asstring()

            # OpenGL 텍스처 생성
            tex_id = glGenTextures(1)
            # glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                img.width(),
                img.height(),
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                data,
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            # glDisable(GL_TEXTURE_2D)

            self.textures[face] = tex_id

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.make_cell_box_texture()

    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, w / h, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        ax = math.radians(self.camera_angle_x)
        ay = math.radians(self.camera_angle_y)
        eye_x = self.camera_distance * math.cos(ax) * math.cos(ay)
        eye_y = self.camera_distance * math.sin(ax) * math.cos(ay)
        eye_z = -self.camera_distance * math.sin(ay)
        gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 0, -1)

        self.draw_background()
        self.draw_global_axis()

        glPushMatrix()
        glTranslatef(0, 0, -2)
        glRotatef(self.z_angle, 0, 0, 1)
        glRotatef(self.y_angle, 0, 1, 0)
        glRotatef(self.x_angle, 1, 0, 0)
        self.draw_cell_box()
        glPopMatrix()

    def updateScene(self):
        if self.euler_angles is not None and self.euler_angles.shape[0] > 0:
            current_euler_angles = self.euler_angles[self.data_index]
            self.x_angle, self.y_angle, self.z_angle = np.degrees(current_euler_angles)
            self.x_angle %= 360
            self.y_angle %= 360
            self.z_angle %= 360
            # print(self.current_time_ms, current_euler_angles)

        self.update()

    def draw_cell_box(self):
        glEnable(GL_TEXTURE_2D)

        # Front face
        glBindTexture(GL_TEXTURE_2D, self.textures["front"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glEnd()

        # Back face
        glBindTexture(GL_TEXTURE_2D, self.textures["back"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glEnd()

        # Left face
        glBindTexture(GL_TEXTURE_2D, self.textures["left"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glEnd()

        # Right face
        glBindTexture(GL_TEXTURE_2D, self.textures["right"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glEnd()

        # Top face
        glBindTexture(GL_TEXTURE_2D, self.textures["top"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, -self.device_height / 2)
        glEnd()

        # Bottom face
        glBindTexture(GL_TEXTURE_2D, self.textures["bottom"])
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 1.0)
        glTexCoord2f(0, 0)
        glVertex3f(self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(1, 0)
        glVertex3f(-self.device_width / 2, -self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(1, 1)
        glVertex3f(-self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glTexCoord2f(0, 1)
        glVertex3f(self.device_width / 2, self.device_depth / 2, self.device_height / 2)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    def draw_global_axis(self):
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # Global X (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.global_axis_length, 0, 0)
        # Global Y (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.global_axis_length, 0)
        # Global Z (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.global_axis_length)
        glEnd()

    def draw_grid(self):
        glColor4f(0.7, 0.7, 0.7, 0.5)
        glBegin(GL_LINES)
        grid_size = int(self.plane_width // 2)
        for i in range(-grid_size, grid_size + 1):
            glVertex3f(i * self.grid_step, -grid_size * self.grid_step, -0.001)
            glVertex3f(i * self.grid_step, grid_size * self.grid_step, -0.001)
            glVertex3f(-grid_size * self.grid_step, i * self.grid_step, -0.001)
            glVertex3f(grid_size * self.grid_step, i * self.grid_step, -0.001)
        glEnd()

    def draw_background(self):
        glDepthMask(GL_FALSE)
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glColor4f(0.3, 0.7, 0.3, 0.5)
        glBegin(GL_QUADS)
        glVertex3f(self.plane_width / 2, self.plane_height / 2, 0)
        glVertex3f(self.plane_width / 2, -self.plane_height / 2, 0)
        glVertex3f(-self.plane_width / 2, -self.plane_height / 2, 0)
        glVertex3f(-self.plane_width / 2, self.plane_height / 2, 0)
        glEnd()
        glPopMatrix()
        glDepthMask(GL_TRUE)
        self.draw_grid()
