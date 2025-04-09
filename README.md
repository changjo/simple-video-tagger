# Simple Video Tagger

## Install Dependencies

```bash
# Recommended to keep dependencies in the project folder
poetry config virtualenvs.in-project true --local

poetry install
```

## Run the App

```bash
poetry run python main.py
```

## Build the App

```bash
poetry run pyinstaller macos.spec --clean --noconfirm
```

Output will be in `dist` folder.
