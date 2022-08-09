import concurrent.futures
import os
from datetime import timedelta, datetime
from typing import Optional, Tuple, Literal, Union, List

import cv2
import numpy

from image_collection import ImageCollection


def calculate_fps(image_names: List[str]) -> float:
    """Uses the images' timestamps to calculate the framerate for creating videos

    Parameters
    ----------
    image_names : List[str]
        A list of names (filenames) from which to pull the timestamps
    """

    dts = [ImageCollection.datetime_from_image_name(name) for name in image_names]
    diff = [dts[i] - dts[i - 1] for i in range(len(dts) - 1, 0, -1)]
    # noinspection PyUnresolvedReferences
    return 1 / numpy.mean(diff).total_seconds()


def single_channel(channel: int, images_dir: Optional[str] = None, output_file: Optional[str] = None,
                   fps: Union[int, Literal['auto']] = 'auto'):
    """Combines all the images in a single channel's directory into one video

    Parameters
    ----------
    channel : int
        The channel to create a video of
    images_dir : str, optional
        The root directory of all the images
    output_file : str, optional
        The filename (or path) of the video to create
    fps : int, 'auto'
        Either a set fps or 'auto' for automatic fps calculation based on how
        long passed between each image capture
    """

    image_folder = os.path.join(images_dir or 'images', f'ch{channel}')
    images = os.listdir(image_folder)
    video_name = output_file or f'ch{channel}.mp4'

    # auto fps calculator
    fps = calculate_fps(images) if fps == 'auto' else fps

    # get the dimensions of the first image to set up the VideoWriter
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    # write all the images to the video
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    # save the video
    video.release()


def all_channels(images_dir: Optional[str] = None, output_file: Optional[str] = None,
                 fps: Union[int, Literal['auto']] = 'auto'):
    """Creates a video made up of ImageCollection image grids from all the images taken

    This function uses the ImageCollection.from_timestamp() class method

    Parameters
    ----------
    images_dir : str, optional
        The root directory of all the images
    output_file : str, optional
        The filename (or path) of the video to create
    fps : int, 'auto'
        Either a set fps or 'auto' for automatic fps calculation based on how
        long passed between each image capture
    """

    ch1_images = os.listdir(os.path.join(images_dir or 'images', 'ch1'))
    video_name = output_file or 'all_channels.mp4'

    # auto fps calculator
    fps = calculate_fps(ch1_images) if fps == 'auto' else fps

    # get the dimensions of one image grid to set up the VideoWriter
    test_frame = ImageCollection.from_index(0).to_cv2_image_grid(2)
    height, width, layers = test_frame.shape
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    # when to start and when to stop is determined by the datetime of the first and last images in ch1
    current_dt = ImageCollection.datetime_from_image_name(ch1_images[0])
    end_dt = ImageCollection.datetime_from_image_name(ch1_images[-1])

    # pre-calculate the datetimes necessary
    total_seconds = (end_dt - current_dt).total_seconds()
    dts = (current_dt + timedelta(seconds=i) for i in numpy.arange(0, total_seconds, fps ** -1))

    # for use in the thread pool
    def create_image_grid(dt: datetime) -> Tuple[datetime, numpy.ndarray]:
        collection = ImageCollection.from_timestamp(dt, 1)
        open_cv_image = collection.to_cv2_image_grid(2)
        return dt, open_cv_image

    # create image grids in a thread pool
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(create_image_grid, dts)

    # write images to a video
    for _, image in sorted(results, key=lambda x: x[0]):
        video.write(image)

    # save the video
    video.release()


def all_channels_basic(images_dir: Optional[str] = None, output_file: Optional[str] = None,
                       fps: Union[int, Literal['auto']] = 'auto'):
    """Creates a video made up of ImageCollection image grids from all the images taken

    This function uses the ImageCollection.from_index() class method

    Parameters
    ----------
    images_dir : str, optional
        The root directory of all the images
    output_file : str, optional
        The filename (or path) of the video to create
    fps : int, 'auto'
        Either a set fps or 'auto' for automatic fps calculation based on how
        long passed between each image capture
    """

    ch1_images = os.listdir(os.path.join(images_dir or 'images', 'ch1'))
    video_name = output_file or 'all_channels.mp4'

    # auto fps calculator
    fps = calculate_fps(ch1_images) if fps == 'auto' else fps

    # get the dimensions of one image grid to set up the VideoWriter
    test_frame = ImageCollection.from_index(0).to_cv2_image_grid(2)
    height, width, layers = test_frame.shape
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    # for use in the thread pool
    def create_image_grid(index: int) -> Tuple[int, numpy.ndarray]:
        collection = ImageCollection.from_index(index)
        open_cv_image = collection.to_cv2_image_grid(2)
        return index, open_cv_image

    # create image grids in a thread pool
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(create_image_grid, range(len(ch1_images)))

    # write images to a video
    for _, image in sorted(results, key=lambda x: x[0]):
        video.write(image)

    # save the video
    video.release()
