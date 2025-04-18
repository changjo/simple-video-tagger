from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("video-tagger")
except PackageNotFoundError:
    import tomli

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        data = tomli.loads(pyproject_path.read_text(encoding="utf-8"))
        __version__ = data["project"]["version"]
    else:
        __version__ = "0.0.0"
