import os
from datetime import datetime, timedelta
from typing import List, Iterable, Optional

import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont

NUM_CAMERAS = 8
PIC_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


class ImageCollection:
    """A class designed to aid in formatting recorded images for later use or presentation

    Attributes
    ----------
    image_paths : List[Optional[str]]
        A list of paths to a single image, one from each channel, or None if one doesn't exist
    """

    def __init__(self, image_paths: List[Optional[str]]):
        """
        Parameters
        ----------
        image_paths : List[Optional[str]]
            A list of paths to a single image, one from each channel, or None if one doesn't exist
        """
        if len(image_paths) != NUM_CAMERAS:
            raise ValueError(f'images_paths parameter must contain {NUM_CAMERAS} image paths')
        elif not any(image_paths):
            raise ValueError('image_paths is blank')
        else:
            self.image_paths = image_paths

    # noinspection PyTypeChecker
    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> numpy.ndarray:
        """Helper method to convert a PIL Image to a cv2-compatible image

        Parameters
        ----------
        pil_image : Image.Image
            The input PIL image to convert

        Returns
        -------
        numpy.ndarray
            The output cv2-compatible image
        """

        image_array = numpy.array(pil_image)
        color_converted = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return color_converted

    @staticmethod
    def cv2_to_pil(cv2_image: numpy.ndarray) -> Image.Image:
        """Helper method to convert a cv2-compatible image to a PIL Image

        Parameters
        ----------
        cv2_image : numpy.ndarray
            The input cv2-compatible image to convert

        Returns
        -------
        numpy.ndarray
            The output PIL Image
        """

        color_converted = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(color_converted)
        return pil_image

    def to_pil_images(self, create_filler_images: bool = True) -> List[Image.Image]:
        """Converts this object's image_paths to a list of PIL Images

        Parameters
        ----------
        create_filler_images : bool, default=True
            Whether to create filler images that say "CH_ is unavailable" if
            a channel's image doesn't exist or just leave as None

        Returns
        -------
        List[Image.Image]
            The resulting PIL Image objects
        """

        # get height and width from an actual image
        if create_filler_images:
            w, h = Image.open(next(filter(lambda x: x is not None, self.image_paths))).size

        resulting_images = []
        for i, image_path in enumerate(self.image_paths):
            if image_path:
                resulting_images.append(Image.open(image_path))
            elif create_filler_images:  # create filler image with channel number in the middle
                # noinspection PyUnboundLocalVariable
                filler_image = Image.new('RGB', (w, h))
                filler_text = ImageDraw.Draw(filler_image)
                filler_font = ImageFont.truetype('arial', w // 20)
                filler_text.text((w / 2, h / 2), f'CH{i + 1} is unavailable', font=filler_font, anchor='mm')
                resulting_images.append(filler_image)
            else:
                resulting_images.append(None)

        return resulting_images

    def to_cv2_images(self, create_filler_images: bool = True) -> List[numpy.ndarray]:
        """Converts this object's image_paths to a list of cv2-compatible images

        Parameters
        ----------
        create_filler_images : bool, default=True
            Whether to create filler images that say "CH_ is unavailable" if
            a channel's image doesn't exist or just leave as None

        Returns
        -------
        List[numpy.ndarray]
            The resulting cv2-compatible image arrays
        """

        # get height and width from an actual image
        if create_filler_images:
            w, h = Image.open(next(filter(lambda x: x is not None, self.image_paths))).size

        resulting_images = []
        for i, image_path in enumerate(self.image_paths):
            if image_path:
                resulting_images.append(cv2.imread(image_path))
            elif create_filler_images:  # create filler image with channel number in the middle
                # noinspection PyUnboundLocalVariable
                filler_image = Image.new('RGB', (w, h))
                filler_text = ImageDraw.Draw(filler_image)
                filler_font = ImageFont.truetype('arial', w // 20)
                filler_text.text((w / 2, h / 2), f'CH{i + 1} is unavailable', font=filler_font, anchor='mm')
                resulting_images.append(self.pil_to_cv2(filler_image))
            else:
                resulting_images.append(None)

        return resulting_images

    def to_pil_image_grid(self, shrink_factor: int = 1) -> Image.Image:
        """Create a 3x3 grid of all the images in image_paths

        Parameters
        ----------
        shrink_factor : int, default=1
            Shrink the images in the grid by this factor, default is no change

        Returns
        -------
        Image.Image
            The resulting PIL Image object of the grid
        """

        # define the grid
        cols = 3
        rows = 3

        # create Image objects from their image paths
        images = self.to_pil_images()

        # shrink the images according to the shrink_factor parameter
        w = images[0].size[0] // shrink_factor
        h = images[0].size[1] // shrink_factor
        images = [image.resize((w, h)) for image in images]

        # create base grid image
        grid = Image.new('RGB', size=(cols * w, rows * h))

        # fill in grid with actual images
        for i, image in enumerate(images):
            grid.paste(image, box=(i % cols * w, i // cols * h))

        return grid

    def to_cv2_image_grid(self, shrink_factor: int = 1) -> numpy.ndarray:
        """Create a 3x3 grid of all the images in image_paths

        Parameters
        ----------
        shrink_factor : int, default=1
            Shrink the images in the grid by this factor, default is no change

        Returns
        -------
        numpy.ndarray
            The resulting cv2-compatible image of the grid
        """

        return self.pil_to_cv2(self.to_pil_image_grid(shrink_factor))

    @staticmethod
    def datetime_from_image_name(image_name: str) -> datetime:
        """Convert an image's filename to a datetime object

        Parameters
        ----------
        image_name : str
            The image name (or filepath) to extract the date and time of capture from

        Returns
        -------
        datetime
            The resulting datetime object from the conversion
        """

        formatted_image_name = os.path.splitext(os.path.basename(image_name))[0]
        return datetime.strptime(formatted_image_name, '%Y-%m-%d %H_%M_%S.%f')

    # noinspection GrazieInspection
    @staticmethod
    def closest_datetime(to: datetime, possibilities: Iterable[datetime]) -> datetime:
        """Get the closest datetime to a target datetime out of a list of possibilities

        Parameters
        ----------
        to : datetime
            The target datetime to compare possibilities to
        possibilities : Iterable[datetime]
            The possible choices for comparison

        Returns
        -------
        datetime
            The resulting chosen datetime from the iterable of possibilities
        """

        return min(possibilities, key=lambda x: abs(x - to))

    @classmethod
    def from_timestamp(cls, timestamp: datetime, max_seconds_apart: int = 1):
        """Get an image from each channel that is closest to the input timestamp

        Parameters
        ----------
        timestamp : datetime
            The target timestamp
        max_seconds_apart : int, default=1
            Ignore images with timestamps too many seconds away from the target,
            even if it's the closest one

        Returns
        -------
        ImageCollection
        """

        resulting_image_paths = []
        for image_dir in PIC_DIRS[1:]:
            possibilities = {cls.datetime_from_image_name(image_name): image_name for image_name in
                             os.listdir(image_dir)}
            if len(possibilities) > 0:
                closest = cls.closest_datetime(timestamp, possibilities.keys())
                if abs(timestamp - closest) <= timedelta(seconds=max_seconds_apart):
                    resulting_image_paths.append(os.path.join(image_dir, possibilities[closest]))
            else:
                resulting_image_paths.append(None)
        return cls(resulting_image_paths)

    @classmethod
    def from_index(cls, index: int):
        """Get an image from each channel that is at a certain index in its directory

        Parameters
        ----------
        index : int
            The index that an image will be pulled from in each channel directory

        Returns
        -------
        ImageCollection
        """

        resulting_image_paths = []
        for image_dir in PIC_DIRS[1:]:
            if len(os.listdir(image_dir)) != 0:
                try:
                    resulting_image_paths.append(os.path.join(image_dir, os.listdir(image_dir)[index]))
                except IndexError:  # index doesn't exist
                    resulting_image_paths.append(None)
            else:  # image_dir is empty
                resulting_image_paths.append(None)
        return cls(resulting_image_paths)
