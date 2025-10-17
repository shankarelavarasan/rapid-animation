import cv2
import os
import numpy as np


def extract_frames(video_path: str, fps: int = 24):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or fps
    interval = max(int(round(src_fps / fps)), 1)
    frames = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            frames.append(frame)
        idx += 1
    cap.release()
    return frames


def merge_3d_frames(frames, output_path: str, fps: int = 24):
    if not frames:
        raise RuntimeError("No frames to merge")
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    for f in frames:
        if f.shape[:2] != (h, w):
            f = cv2.resize(f, (w, h))
        writer.write(f)
    writer.release()
    return output_path