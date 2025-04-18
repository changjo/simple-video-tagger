import os
from dataclasses import dataclass

import yaml


@dataclass
class DataConfig:
    """Configuration class for the video tagging application.

    Attributes:
        video_start_time_utc (str): Start time of the video in UTC format.
        video_path (str): Path to the video file.
    """

    video_start_time_utc: str
    video_path: str
    db_path: str
    imu_action_path: str
    fusion_data_path: str = ""


def load_data_config(config_path: str) -> DataConfig:
    """Load the configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        Config: An instance of the Config class with loaded settings.
    """

    if not os.path.exists(config_path):
        db_path = os.path.join(os.path.dirname(config_path), "tags.db")
        return DataConfig(
            video_start_time_utc="",
            video_path="",
            db_path=db_path,
            imu_action_path="",
            fusion_data_path="",
        )

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return DataConfig(**data)


def save_data_config(config: DataConfig, config_path: str):
    """Save the configuration to a YAML file.

    Args:
        config (Config): An instance of the Config class with settings to save.
        config_path (str): Path to the configuration file.
    """
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.__dict__, f, allow_unicode=True)
