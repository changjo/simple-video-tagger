import json
import os
from typing import Optional

import pandas as pd
import yaml


def load_settings(filename=None):
    if filename is None or not os.path.exists(filename):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_dir, "config", "settings.yaml")
    else:
        config_path = filename

    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_settings(data, filename):
    print(filename)
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    print(f"Saved settings to {filename}")


def format_time(ms, show_miliseconds=True):
    sign = "-" if ms < 0 else ""
    ms = abs(ms)
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    time_format = f"{m:02d}:{s:02d}"
    if h > 0:
        time_format = f"{h:02d}:" + time_format
    else:
        time_format = "00:" + time_format

    if show_miliseconds:
        miliseconds = ms % 1000
        time_format += f".{miliseconds:03d}"

    return sign + time_format


def load_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_fusion_data(filename: str):
    df = pd.read_csv(filename, parse_dates=["datetime"])
    return df


def get_video_time_ms(
    datetimes: pd.Series, video_start_time_utc: Optional[pd.Timestamp]
) -> pd.Series:
    if video_start_time_utc is None:
        return pd.Series([0] * len(datetimes))
    return ((datetimes - video_start_time_utc).dt.total_seconds() * 1000).astype(int)
