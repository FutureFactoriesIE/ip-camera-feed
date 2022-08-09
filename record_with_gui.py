import time
import tkinter as tk
from datetime import timedelta
from tkinter.messagebox import askyesno
from typing import Optional

from PIL import Image, ImageDraw, ImageTk

from recorder import Recorder

NUM_CAMERAS = 8
CAPTURE_DELAY = 0.5  # in seconds
DT_OFFSET = 3  # in seconds

IMAGE_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]


class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        self.title('ip-camera-feed')
        self.rowconfigure(0, weight=1)
        self.geometry('300x50')

        self.record_label = tk.Label(self, text='Click to start recording ->')
        self.record_label.grid(column=0, row=0, padx=5, pady=5)
        self.columnconfigure(0, weight=1)

        image_size = 25
        image = Image.new('RGBA', (image_size, image_size))
        draw = ImageDraw.Draw(image)
        draw.ellipse((0, 0, image_size, image_size), fill='red')
        image = ImageTk.PhotoImage(image)
        self.record_button = tk.Button(self, image=image, command=self.on_record_button_click)
        self.record_button.image = image  # retain image so it isn't garbage collected
        self.record_button.grid(column=1, row=0, padx=5, pady=5)

        self.recorder: Optional[Recorder] = None
        self.recording_start_time = 0  # in seconds

    def on_record_button_click(self):
        if self.recorder is None:
            delete_old_images = askyesno('Question', 'Do you want to delete the old images?')
            verbose = askyesno('Question', 'Enable verbose output?')

            # config GUI part 1
            self.record_label.config(text='Initializing cameras...')
            self.record_button.config(state=tk.DISABLED)
            self.update()

            # start recording
            self.recorder = Recorder(IMAGE_DIRS, NUM_CAMERAS, DT_OFFSET, CAPTURE_DELAY, delete_old_images, verbose)
            self.recorder.start_recording()
            self.recording_start_time = time.time()
            self.update()  # pass through any clicks during "not responding" stage

            # config GUI part 2
            self.record_label.config(text='0:00:00 Click to stop recording ->')
            self.record_button.config(state=tk.NORMAL)
            image_size = 25
            padding = 5
            image = Image.new('RGBA', (image_size, image_size))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0 + padding, 0 + padding, image_size - padding, image_size - padding), fill='red')
            image = ImageTk.PhotoImage(image)
            self.record_button.config(image=image)
            self.record_button.image = image

            # start update loop
            self.after(1000, self.update_text)
        else:
            # stop recording
            self.recorder.stop_recording()
            self.recorder = None

            # config GUI
            self.record_label.config(text='Click to start recording ->')
            image_size = 25
            image = Image.new('RGBA', (image_size, image_size))
            draw = ImageDraw.Draw(image)
            draw.ellipse((0, 0, image_size, image_size), fill='red')
            image = ImageTk.PhotoImage(image)
            self.record_button.config(image=image)
            self.record_button.image = image
            self.record_button.grid(column=1, row=0, padx=5, pady=5)

    def update_text(self):
        time_elapsed = timedelta(seconds=int(time.time() - self.recording_start_time))
        self.record_label.config(text=f'{time_elapsed} Click to stop recording ->')
        if self.recorder is not None:
            self.after(1000, self.update_text)
        else:
            self.record_label.config(text='Click to start recording ->')


if __name__ == '__main__':
    app = App()
    app.mainloop()
