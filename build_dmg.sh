#!/usr/bin/env bash

pyinstaller macos.spec --clean --noconfirm

/opt/homebrew/bin/create-dmg \
    --volname "Simple Video Tagger" \
    --volicon resources/icons/icon.png \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --app-drop-link 650 185 \
    "dist/SimpleVideoTagger.dmg" \
    dist/SimpleVideoTagger.app
