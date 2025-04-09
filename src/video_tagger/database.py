import os
import sqlite3


class TagDatabase:
    def __init__(self, db_path="data/tagged_data/tags.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tags (
                    time_ms INTEGER,
                    tag_name TEXT,
                    tag_type TEXT,
                    PRIMARY KEY (time_ms, tag_name, tag_type)
                )
            """
            )
            # Create composite index for both columns
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_time_tag
                ON tags(time_ms ASC, tag_name ASC)
            """
            )
            # Create individual index for tag_name for tag-based searches
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tag_name
                ON tags(tag_name ASC)
            """
            )
            conn.commit()

    def load_tags(self):
        if not os.path.exists(self.db_path):
            print(f'"{self.db_path}" Database not found')
            return []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT time_ms, tag_name, tag_type FROM tags INDEXED
                BY idx_time_tag
                ORDER BY time_ms, tag_name, tag_type
                """
            )
            return cursor.fetchall()

    def add_tag(self, time_ms, tag_name, tag_type):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO tags (time_ms, tag_name, tag_type) VALUES (?, ?, ?)",
                (time_ms, tag_name, tag_type),
            )
            conn.commit()

    def remove_tag(self, time_ms, tag_name, tag_type):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tags WHERE time_ms = ? AND tag_name = ? AND tag_type = ?",
                (time_ms, tag_name, tag_type),
            )
            conn.commit()

    def find_tags_by_name(self, tag_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT time_ms, tag_name, tag_type FROM tags
                WHERE tag_name LIKE ? ORDER BY time_ms
                """,
                (f"%{tag_name}%",),
            )
            return cursor.fetchall()
