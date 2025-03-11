# my_video_tagger/main.py
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from src.video_tagger.utils import load_settings
from src.video_tagger.video_tagger import VideoTagger


def main():
    app = QApplication(sys.argv)
    config = load_settings()

    global_font_name = config.get("app", {}).get("font", "Arial").get("name", "Arial")
    global_font_size = config.get("app", {}).get("font", 12).get("size", 12)

    font = QFont(global_font_name, global_font_size)

    app.setFont(font)

    window = VideoTagger(config)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
