import os.path
import shutil
import time
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import List, Iterable

import cv2

NUM_CAMERAS = 8
PIC_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


class Camera(Thread):
    def __init__(self, index: int, stop_event: Event):
        Thread.__init__(self)
        self.daemon = True
        self._stop_event = stop_event
        self._client = cv2.VideoCapture(f'rtsp://admin:123456@10.43.3.113/ch0{index}/0')
        print(f'Connected to ch{index}')
        self._image_dir = f'images\\ch{index}'

    def run(self) -> None:
        start_time = time.time()
        while not self._stop_event.is_set():
            success, frame = self._client.read()
            if time.time() - start_time >= 0.5 and success:
                filename = str(datetime.now()).replace(':', '_') + '.jpg'
                cv2.imwrite(os.path.join(self._image_dir, filename), frame)
                start_time = time.time()
            # time.sleep(max(0.5 - (time.time() - start_time), 0))
        self._client.release()


def create_directories():
    for missing_dir in filter(lambda x: not os.path.isdir(x), PIC_DIRS):
        os.mkdir(missing_dir)


def delete_images():
    shutil.rmtree('../images')


def datetime_from_image_name(image_name: str) -> datetime:
    return datetime.strptime(os.path.splitext(image_name)[0], '%Y-%m-%d %H_%M_%S.%f')


def closest_datetime(to: datetime, possibilities: Iterable[datetime]) -> datetime:
    return min(possibilities, key=lambda x: abs(x - to))


def get_images(dt: datetime, max_seconds_apart: int = 1) -> List[str]:
    results = []
    for image_dir in PIC_DIRS[1:]:
        possibilities = {datetime_from_image_name(image_name): image_name for image_name in os.listdir(image_dir)}
        if len(possibilities) > 0:
            closest = closest_datetime(dt, possibilities.keys())
            if abs(dt - closest) <= timedelta(seconds=max_seconds_apart):
                results.append(os.path.join(image_dir, possibilities[closest]))
    return results


def askyesno(question: str) -> bool:
    inpt = ''
    while inpt not in ['y', 'n']:
        inpt = input(question).lower()
    return inpt == 'y'


if __name__ == '__main__':
    if askyesno('Delete old images? [y/n] '):
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
