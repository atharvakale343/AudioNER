#!/bin/bash

python src/audioNER/app_server.py &

sleep 3

python src/audioNER/app_client.py --audio_files data/harrypotter.mp3 data/cybertruck.mp3 data/georgewashington.mp3

