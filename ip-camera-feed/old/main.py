import os.path
import shutil
import time
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import List, Iterable

import rtsp


NUM_CAMERAS = 8


class Camera(Thread):
    def __init__(self, index: int, stop_event: Event):
        Thread.__init__(self)
        self._stop_event = stop_event
        self._client = rtsp.Client(rtsp_server_uri=f'rtsp://admin:123456@10.43.3.113/ch0{index}/0', verbose=True)
        self._image_dir = f'images\\ch{index}'

    def run(self) -> None:
        while not self._stop_event.is_set():
            image = self._client.read()
            if image is not None:
                filename = str(datetime.now()).replace(':', '_') + '.png'
                image.save(os.path.join(self._image_dir, filename))
            time.sleep(0.1)
        self._client.close()


def create_directories():
    try:
        os.mkdir('../images')
        for i in range(NUM_CAMERAS):
            os.mkdir(f'images\\ch{i + 1}')
    except FileExistsError:
        pass


def delete_images():
    shutil.rmtree('../images')


def datetime_from_image_name(image_name: str) -> datetime:
    return datetime.strptime(os.path.splitext(image_name)[0], '%Y-%m-%d %H_%M_%S.%f')


def closest_datetime(to: datetime, possibilities: Iterable[datetime]) -> datetime:
    return min(possibilities, key=lambda x: abs(x - to))


def get_images(dt: datetime, max_seconds_apart: int) -> List[str]:
    results = []
    for image_dir in [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]:
        possibilities = {datetime_from_image_name(image_name): image_name for image_name in os.listdir(image_dir)}
        if len(possibilities) > 0:
            closest = closest_datetime(dt, possibilities.keys())
            if abs(dt - closest) <= timedelta(seconds=max_seconds_apart):
                results.append(os.path.join(image_dir, possibilities[closest]))
    return results


if __name__ == '__main__':
    delete_images()
    create_directories()
    stop_recording_event = Event()
    cameras = [Camera(i + 1, stop_recording_event) for i in range(NUM_CAMERAS)]
    print('Starting to record')
    for camera in cameras:
        camera.start()
    input('Press ENTER to stop recording')
    stop_recording_event.set()
    for camera in cameras:
        camera.join()
    print('Finished recording')
