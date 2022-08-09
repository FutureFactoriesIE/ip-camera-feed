import os
from datetime import timedelta
from typing import Optional

import cv2
import numpy
from PIL import Image

from image_collection import ImageCollection


def single_channel(channel: int, images_dir: Optional[str], output_file: Optional[str] = None):
    """Combines all the images in a single channel's directory into one video"""
    image_folder = os.path.join(images_dir or 'images', f'ch{channel}')
    video_name = output_file or f'ch{channel}.mp4'

    # get the dimensions of the first image to set up the VideoWriter
    images = os.listdir(image_folder)
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    # write all the images to the video
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    # save the video
    video.release()


def all_channels(images_dir: Optional[str] = None, output_file: Optional[str] = None, verbose: bool = True):
    """Creates a video made up of ImageCollection image grids from all the images taken"""
    ch1_images = os.listdir(os.path.join(images_dir or 'images', 'ch1'))
    video_name = output_file or 'all_channels.mp4'

    # shrinks the image grids by a factor of 2, otherwise the video won't play
    def resized_image(image: numpy.ndarray) -> numpy.ndarray:
        shrink_factor = 2
        h, w, _ = image.shape
        return cv2.resize(image, (w // shrink_factor, h // shrink_factor))

    # converts a PIL Image object to a cv2-compatible numpy array
    # noinspection PyTypeChecker
    def pil_to_cv2(pil_image: Image.Image) -> numpy.ndarray:
        image_array = numpy.array(pil_image)
        color_converted = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return color_converted

    # get the dimensions of one image grid to set up the VideoWriter
    test_frame = resized_image(pil_to_cv2(ImageCollection.from_index(0).to_pil_image_grid()))
    height, width, layers = test_frame.shape
    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    # when to start and when to stop is determined by the datetime of the first and last images in ch1
    current_dt = ImageCollection.datetime_from_image_name(ch1_images[0])
    end_dt = ImageCollection.datetime_from_image_name(ch1_images[-1])

    # continue writing images until time has expired
    total_seconds = int((end_dt - current_dt).total_seconds())
    while end_dt - current_dt >= timedelta(seconds=0):
        collection = ImageCollection.from_timestamp(current_dt, 1)
        open_cv_image = resized_image(pil_to_cv2(collection.to_pil_image_grid()))
        video.write(open_cv_image)
        current_dt += timedelta(seconds=1)
        print(f'\r{int(total_seconds - (end_dt - current_dt).total_seconds()) + 1}/{total_seconds + 1} images written')

    # save the video
    video.release()
