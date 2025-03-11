import json
import os

import yaml


def load_settings():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(base_dir, "config", "settings.yaml")

    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else {}


def format_time(ms, show_miliseconds=True):
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    time_format = f"{m:02d}:{s:02d}"
    if h > 0:
        time_format = f"{h:02d}:" + time_format

    if show_miliseconds:
        miliseconds = ms % 1000
        time_format += f".{miliseconds:03d}"

    return time_format


def load_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
