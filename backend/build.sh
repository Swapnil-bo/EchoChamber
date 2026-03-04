#!/bin/bash
# Render build script.
# ffmpeg is pre-installed on Render's native Python environments.
# Do NOT add apt-get installs — Render does not grant root access
# in build scripts and it will fail with Permission Denied.
pip install -r requirements.txt
