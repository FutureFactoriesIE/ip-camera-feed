import os.path
import shutil
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import List, Iterable
from queue import Queue, Empty

import cv2

NUM_CAMERAS = 8
PIC_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


class Camera(Thread):
    def __init__(self, index: int, stop_event: Event, image_queue: Queue):
        Thread.__init__(self)
        self.index = index
        self._stop_event = stop_event
        self._image_queue = image_queue
        self._client = cv2.VideoCapture(f'rtsp://admin:123456@10.43.3.113/ch0{self.index}/0')
        print(f'Connected to ch{self.index}')
        self._image_dir = f'images\\ch{self.index}'

    def run(self) -> None:
        while not self._stop_event.is_set():
            success, frame = self._client.read()
            if success and self._client.get(cv2.CAP_PROP_POS_MSEC) % 500 == 0:
                timestamp = str(datetime.now()).replace(':', '_')
                self._image_queue.put((self.index, timestamp, frame))
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

    stop_event = Event()
    image_queue = Queue()
    cameras = [Camera(i + 1, stop_event, image_queue) for i in range(NUM_CAMERAS)]
    print('Starting to record')
    for camera in cameras:
        camera.start()
    input('Press ENTER to stop recording')
    stop_event.set()
    for camera in cameras:
        camera.join()
    print('Finished recording')
    print('Saving images')
    while True:
        try:
            index, timestamp, frame = image_queue.get_nowait()
        except Empty:
            break
        cv2.imwrite(f'images\\ch{index}\\{timestamp}.jpg', frame)
    print('Done')
