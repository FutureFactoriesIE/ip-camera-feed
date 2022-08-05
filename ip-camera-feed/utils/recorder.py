import os
import shutil
import time
from datetime import timedelta, datetime
from threading import Event, Thread
from typing import Optional, List

import rtsp


class Recorder:
    def __init__(self, image_dirs: List[str], num_cameras: int, dt_offset: float, capture_delay: float,
                 delete_old_images: bool = True, verbose: bool = True):
        self.image_dirs = image_dirs
        self.num_cameras = num_cameras
        self.dt_offset = dt_offset
        self.capture_delay = capture_delay
        self.verbose = verbose

        # delete the entire images directory
        if delete_old_images:
            shutil.rmtree('images')

        # add any directories that should exist
        for missing_dir in filter(lambda x: not os.path.isdir(x), self.image_dirs):
            os.mkdir(missing_dir)

        # connect to all the cameras
        if self.verbose:
            print('Initializing cameras')
        self.cameras = [rtsp.Client(f'rtsp://admin:123456@10.43.3.113/ch0{i + 1}/0', verbose=self.verbose) for i in
                        range(self.num_cameras)]

        self._recorder_thread: Optional[Thread] = None
        self._stop_recording_event = Event()

    def start_recording(self):
        if self.verbose:
            print('Starting to record')

        def record():
            while not self._stop_recording_event.is_set():
                iter_time = time.time()
                for i, camera in enumerate(self.cameras):
                    img = camera.read()
                    if img is not None:
                        timestamp = str(datetime.now() + timedelta(seconds=self.dt_offset)).replace(':', '_')
                        img.save(f"{self.image_dirs[1:][i]}\\{timestamp}.jpg")
                time.sleep(max(0.0, self.capture_delay - (time.time() - iter_time)))

        self._recorder_thread = Thread(target=record)
        self._recorder_thread.start()

    def stop_recording(self):
        self._stop_recording_event.set()
        self._recorder_thread.join()  # wait for thread to finish

        # disconnect from the cameras
        if self.verbose:
            print('Finished recording')
        for camera in self.cameras:
            camera.close()
