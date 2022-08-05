import os
from datetime import datetime, timedelta
from typing import List, Iterable

from PIL import Image, ImageDraw, ImageFont

NUM_CAMERAS = 8
PIC_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


class ImageCollection:
    def __init__(self, image_paths: List[str]):
        if len(image_paths) != NUM_CAMERAS:
            raise Exception(f'images_paths parameter must contain {NUM_CAMERAS} image paths')
        elif not any(image_paths):
            raise Exception('image_paths is blank')
        else:
            self.image_paths = image_paths

    def to_images(self) -> List[Image.Image]:
        # get height and width from an actual image
        w, h = Image.open(next(filter(lambda x: x is not None, self.image_paths))).size

        resulting_images = []
        for i, image_path in enumerate(self.image_paths):
            if image_path:
                resulting_images.append(Image.open(image_path))
            else:  # create filler image with channel number in the middle
                filler_image = Image.new('RGB', (w, h))
                filler_text = ImageDraw.Draw(filler_image)
                filler_font = ImageFont.truetype('arial', w // 20)
                filler_text.text((w / 2, h / 2), f'CH{i + 1} is unavailable', font=filler_font, anchor='mm')
                resulting_images.append(filler_image)
        return resulting_images

    def to_image_grid(self, shrink_factor: int = 1) -> Image.Image:
        # define the grid
        cols = 3
        rows = 3

        # create Image objects from their image paths
        images = self.to_images()

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

    @staticmethod
    def datetime_from_image_name(image_name: str) -> datetime:
        return datetime.strptime(os.path.splitext(image_name)[0], '%Y-%m-%d %H_%M_%S.%f')

    @staticmethod
    def closest_datetime(to: datetime, possibilities: Iterable[datetime]) -> datetime:
        return min(possibilities, key=lambda x: abs(x - to))

    @classmethod
    def from_timestamp(cls, timestamp: datetime, max_seconds_apart: int = 1):
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
        resulting_image_paths = []
        for image_dir in PIC_DIRS[1:]:
            if len(os.listdir(image_dir)) != 0:
                resulting_image_paths.append(os.path.join(image_dir, os.listdir(image_dir)[index]))
            else:
                resulting_image_paths.append(None)
        return cls(resulting_image_paths)
