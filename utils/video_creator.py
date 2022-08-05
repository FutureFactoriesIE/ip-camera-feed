import os
from datetime import timedelta
from typing import Optional

import cv2
import numpy

from image_collection import ImageCollection


def single_channel(channel: int, images_dir: str, output_file: Optional[str] = None):
    image_folder = os.path.join(images_dir, f'ch{channel}')
    video_name = output_file or f'ch{channel}.mp4'

    images = os.listdir(image_folder)
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    video.release()


def all_channels(images_dir: str, output_file: Optional[str] = None):
    ch1_path = os.path.join(images_dir, 'ch1')
    video_name = output_file or 'all_channels.mp4'

    def resized_image(image: numpy.ndarray):
        shrink_factor = 2
        h, w, _ = image.shape
        return cv2.resize(image, (w // shrink_factor, h // shrink_factor))

    frame = resized_image(cv2.cvtColor(numpy.array(ImageCollection.from_index(0).to_image_grid()), cv2.COLOR_RGB2BGR))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    current_dt = ImageCollection.datetime_from_image_name(os.listdir(ch1_path)[0])
    end_dt = ImageCollection.datetime_from_image_name(os.listdir(ch1_path)[-1])
    while end_dt - current_dt > timedelta(seconds=0):
        collection = ImageCollection.from_timestamp(current_dt, 1)
        open_cv_image = resized_image(cv2.cvtColor(numpy.array(collection.to_image_grid()), cv2.COLOR_RGB2BGR))
        video.write(open_cv_image)
        current_dt += timedelta(seconds=1)

    video.release()
