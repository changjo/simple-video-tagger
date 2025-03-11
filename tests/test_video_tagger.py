# my_video_tagger/tests/test_video_tagger.py
from src.video_tagger.tag_manager import TagManager


def test_tag_manager():
    manager = TagManager()
    manager.add_tag("Test Tag")
    assert len(manager.get_tags()) == 1
    assert manager.get_tags()[0] == "Test Tag"
