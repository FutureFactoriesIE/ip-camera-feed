from recorder import Recorder

NUM_CAMERAS = 8
CAPTURE_DELAY = 0.5  # in seconds
DT_OFFSET = 4  # in seconds

IMAGE_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


def askyesno(question: str) -> bool:
    inpt = ''
    while inpt not in ['y', 'n']:
        inpt = input(question).lower()
    return inpt == 'y'


if __name__ == '__main__':
    delete_old_images = askyesno('Do you want to delete the old images? [y/n] ')
    verbose = askyesno('Enable verbose output? [y/n] ')

    recorder = Recorder(IMAGE_DIRS, NUM_CAMERAS, DT_OFFSET, CAPTURE_DELAY, delete_old_images, verbose)
    recorder.start_recording()
    input('Press ENTER to stop recording')
    recorder.stop_recording()
