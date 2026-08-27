#!/bin/bash

SCRIPT_PATH=$1

blender -b -P $SCRIPT_PATH --render-output /tmp/output --render-format FFMPEG --render-anim

echo "Rendered to /tmp/output.mp4"
