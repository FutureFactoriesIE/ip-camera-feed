import os
import shutil
import time
from datetime import timedelta, datetime
from threading import Event, Thread
from typing import Optional, List

import rtsp


class Recorder:
    """A class that uses threading to capture and save images in the background

    Attributes
    ----------
    image_dirs : List[str]
        The paths of both the root image directory and the channel directories
    num_cameras : int
        How many cameras there are
    dt_offset : float
        How many seconds to add (or subtract if the number is negative) to the timestamp
        of the images to better align with the actual timestamps pasted on the images themselves
    capture_delay : float
        How many seconds to wait in between capturing images
    delete_old_images : bool, default=True
        Whether to delete the existing "images" directory (if True, the entirety of the directory
        listed as the first index of image_dirs will be deleted)
    verbose : bool, default=True
        Whether to log to the console information about what is happening while the script is running
    cameras : List[rtsp.Client]
        The Client objects that directly capture frames from cv2's RTSP buffer
    _recorder_thread : threading.Thread
        The thread that handles saving captured images to the disk
    _stop_recording_event : threading.Event
        An event that notifies the _recorder_thread to stop
    """

    def __init__(self, image_dirs: List[str], num_cameras: int, dt_offset: float, capture_delay: float,
                 delete_old_images: bool = True, verbose: bool = True):
        """
        Parameters
        ----------
        image_dirs : List[str]
            The paths of both the root image directory and the channel directories
        num_cameras : int
            How many cameras there are
        dt_offset : float
            How many seconds to add (or subtract if the number is negative) to the timestamp
            of the images to better align with the actual timestamps pasted on the images themselves
        capture_delay : float
            How many seconds to wait in between capturing images
        delete_old_images : bool, default=True
            Whether to delete the existing "images" directory (if True, the entirety of the directory
            listed as the first index of image_dirs will be deleted)
        verbose : bool, default=True
            Whether to log to the console information about what is happening while the script is running
        """

        self.image_dirs = image_dirs
        self.num_cameras = num_cameras
        self.dt_offset = dt_offset
        self.capture_delay = capture_delay
        self.verbose = verbose

        # delete the entire images directory if it exists
        if delete_old_images:
            try:
                shutil.rmtree(self.image_dirs[0])
            except FileNotFoundError:
                pass

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
        """Start recording and saving images to the disk"""

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
                # wait for capture delay to take more pics, accounting for the amount of time it took to take the pics
                time.sleep(max(0.0, self.capture_delay - (time.time() - iter_time)))

        self._recorder_thread = Thread(target=record)
        self._recorder_thread.start()

    def stop_recording(self):
        """Stop recording and saving images to the disk"""

        self._stop_recording_event.set()
        self._recorder_thread.join()  # wait for thread to finish

        # disconnect from the cameras
        if self.verbose:
            print('Finished recording')
        for camera in self.cameras:
            camera.close()
