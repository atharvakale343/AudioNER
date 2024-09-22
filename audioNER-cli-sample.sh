#!/bin/bash

python src/audioNER/app_server.py &

sleep 3

audioNER-cli --audio_files data/audio.mp3 data/news.mp3

