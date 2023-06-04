#!/usr/bin/env python
from ffmpeg.video import video_trans_img
import argparse
import subprocess
import re
import os
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File deleted: {file_path}")
    except OSError as e:
        print(f"Error deleting file: {e}")
def extract_screen_cap(video_path, frame, output_path):
    #shell command
    #ffmpeg -ss 15 -i twitch_nft_demo.mp4 -vf "scale=96:74" -vframes 1 images3.jpg
    #input_file, out_path, img_prefix, category="png"
    try:
        command = ['ffmpeg', '-ss', frame, '-i', video_path, '-vf','scale=96:74', '-vframes', '1', output_path]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Screenshot extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error outputting frames: {e}")
        return None
def get_total_frames(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'default=nokey=1:noprint_wrappers=1', video_path]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        total_frames = int(output)
        return total_frames
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving total frames: {e}")
        return None
def get_video_fps(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8').strip()
        numerator, denominator = re.match(r'(\d+)/(\d+)', output).groups()
        fps = float(numerator) / float(denominator)
        return fps
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving video FPS: {e}")
        return None
start = 'screenshots/start.png'
middle = 'screenshots/middle.png'
end = 'screenshots/end.png'
start_frame = 1
middle_frame = 2959
end_frame = 5919
#delete_file(start)
#delete_file(middle)
#delete_file(end)
input_path = 'twitch_nft_demo.mp4'
frames = get_total_frames(input_path)
fps = get_video_fps(input_path)
if fps is not None:
    print(f"Video FPS: {fps}")
if frames is not None:
    print(f"Total frames: {frames}")
output_path = 'screenshots/images.jpg'  # Specify the output path for the screen capture image
extract_screen_cap(input_path, str(start_frame), output_path)