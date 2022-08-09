# ip-camera-feed
This module simplifies and streamlines collecting frames from the cell’s 8 IP cameras. It also includes submodules for extra functionality for working with recorded images including creating videos, creating a grid of all 8 cameras, finding images that are closest to a specified date, and more.

This README is a word-for-word copy of my original User Guide which can be found [here](https://docs.google.com/document/d/17rf1jWHrGiAbOEz-Kpk1TVBcSjudw_ltXglgl5a6eaU/edit?usp=sharing).

Actual documentation can be found [here](https://sites.google.com/view/ip-camera-feed-docs/home).

## Recording
There are two ways to record frames using the ip-camera-feed module.
1. [record_with_cmd.py](record_with_cmd.py) - a completely command-line focused application that runs once; this script starts recording immediately after it is run, waits for the user to click ENTER, and then stops recording
2. [record_with_gui.py](record_with_gui.py) - a GUI based application that can be used for recording multiple times without having to stop and restart the script; this script opens a GUI, waits for its record button to be pressed, starts recording, waits for the stop button to be pressed, stops recording, and then idles until the record button is clicked again (this script also displays how long it has been recording for)

To actually record, all you need to do is just run one of the above scripts in a Python environment.

***Note: Neither is more efficient than the other; it is solely up to preference.***


## Configuring the Recording
There are a few settings that can be edited before executing a script to allow for different recording situations.
```python
...
NUM_CAMERAS = 8
CAPTURE_DELAY = 0.5  # in seconds
DT_OFFSET = 4  # in seconds
...
```

In both [record_with_cmd.py](record_with_cmd.py) and [record_with_gui.py](record_with_gui.py), there exist 3 global variables at the top:
1. [`NUM_CAMERAS`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/record_with_gui.py#L11) - how many cameras there are
2. [`CAPTURE_DELAY`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/record_with_gui.py#L12) - how many seconds to wait in between capturing images
3. [`DT_OFFSET`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/record_with_gui.py#L13) - how many seconds to add (or subtract if the number is negative) to the timestamp of the images to better align with the actual timestamps pasted on the images themselves

```python
...
IMAGE_DIRS = ['images'] + [f'images\\ch{i + 1}' for i in range(NUM_CAMERAS)]
...
```

There is another global variable at the top of each script, `IMAGE_DIRS`, but this should not be changed.

Two questions are also asked at runtime that don’t directly affect the recording but rather the user experience:
1. **Do you want to delete the old images?** - deletes the images directory
2. **Enable verbose output?** - logs to the console information about what is happening while the script is running


## Creating Videos
Previously recorded frames can be converted into videos using the video_creator module.
Three public functions are available for use:
1. [`single_channel()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/video_creator.py#L27) - combines all the images in a single channel's directory into one video
2. [`all_channels()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/video_creator.py#L64) - creates a video made up of ImageCollection image grids organized using the ImageCollection.from_timestamp() class method
3. [`all_channels_basic()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/video_creator.py#L118) - creates a video made up of ImageCollection image grids organized using the ImageCollection.from_index() class method

Creating a video of channel 3 is as simple as:

```python
from video_creator import single_channel
single_channel(3, 'images')
```

And creating a video of all of the channels in a grid format is as simple as:

```python
from video_creator import all_channels
all_channels('images')
```

Refer to the [documentation](https://sites.google.com/view/ip-camera-feed-docs/video_creator) for more information on the [video_creator](video_creator.py) submodule.


## Working with Recorded Images
The [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) class exists to aid in formatting recorded images for later use or presentation.

Creating an [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) object should only be done by using its class method constructors, like [`from_timestamp()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L235) and [`from_index()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L264).
1. [`from_timestamp()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L235) - creates an [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) object with an image from each channel that is closest to the input timestamp (a datetime object)
2. [`from_index()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L264) - creates an [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) object with the image from each channel directory at the specified index

For example, creating an [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) object with images from each channel that is close to 08/12/2022 at 09:45:00 can be done by:

```python
from image_collection import ImageCollection
collection = ImageCollection.from_timestamp(datetime(2022, 8, 12, 9, 45))
```

To use recorded images in scripts, methods such as [`to_pil_images()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L75) or [`to_cv2_images()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L110) can be used. The default behavior of these methods is to create filler images for the channels that don’t have an image, but this can be overridden by setting the `create_filler_images` parameter to `False`.

```python
collection.to_pil_images()
```
```
[<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2592x1944 at 
0x292AE2B5850>, <PIL.Image.Image [...]
```

Creating a grid of all of the channels in one image is as simple as:

```python
collection.to_pil_image_grid()
```
```
<PIL.Image.Image image mode=RGB size=7776x5832 at 0x292AF6DE9D0>
```

You can also get a cv2-compatible image grid using:

```python
collection.to_cv2_image_grid()
```
```
array([[[122, 130, 123], [113, 121, 114], [...]
```

For convenience, [`ImageCollection`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L13) even has static methods that facilitate conversion between PIL Images and cv2 images:

```python
ImageCollection.pil_to_cv2()
ImageCollection.cv2_to_pil()
```

And another static method for grabbing a datetime object from a recorded image’s filename:

```python
ImageCollection.datetime_from_image_name('images/ch8/2022-08-08 11_14_44.126554.jpg')
```
```
datetime.datetime(2022, 8, 8, 11, 14, 44, 126554)
```

Just like the [record_with_cmd.py](record_with_cmd.py) and [record_with_gui.py](record_with_gui.py) scripts, there exists the global variable [`NUM_CAMERAS`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/image_collection.py#L9) at the top of [image_collection.py](image_collection.py) that can be edited if necessary.

Refer to the [documentation](https://sites.google.com/view/ip-camera-feed-docs/image_collection) for more information on the [image_collection](image_collection.py) submodule.


## Advanced Usage
For use cases that are more involved than the two included scripts, [record_with_cmd.py](record_with_cmd.py) and [record_with_gui.py](record_with_gui.py), using the [`Recorder`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/recorder.py#L11) class from the [recorder](recorder.py) module directly is necessary.

Its usage is very straightforward, as it only has two methods: [`start_recording()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/recorder.py#L85) and [`stop_recording()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/recorder.py#L105). Additionally, its constructor parameters are almost identical to the explanation in the [**Configuring the Recording**](#configuring-the-recording) section of this User Guide.

The sole difference is the `image_dirs` parameter. Its type must be a `List[str]` and must contain the root directory of the images for its first index and the channel subdirectories (in order) for its remaining indices. Examples can be found at the top of [record_with_cmd.py](record_with_cmd.py) and [record_with_gui.py](record_with_gui.py).

Recorder objects are threaded, meaning a call to [`stop_recording()`](https://github.com/FutureFactoriesIE/ip-camera-feed/blob/ba40e568fcbd97b404769b71acf0ca74e25070c1/recorder.py#L105) will not block.

Below is an example of waiting for user input to start recording and then waiting for 200 images to be captured before stopping the recording. A different directory structure is used as well.

```python
import os
from recorder import Recorder

IMAGE_DIRS = ['parent/images'] + [f'parent/images/camera{i + 1}' for i in range(8)]

if __name__ == '__main__':
    recorder = Recorder(IMAGE_DIRS, 8, 4, 0.5, True, True)
    input('Click ENTER to start recording')
    recorder.start_recording()
    while len(os.listdir('parent/images/camera1')) < 200:
        pass  # or do something productive
    recorder.stop_recording()
```

Refer to the [documentation](https://sites.google.com/view/ip-camera-feed-docs/recorder) for more information on the [recorder](recorder.py) submodule.


## Examples
To record for a set amount of time rather than having to stop the recording manually, edit [record_with_cmd.py](record_with_cmd.py) as follows:

```python
[...]
recorder = Recorder(IMAGE_DIRS, NUM_CAMERAS, DT_OFFSET, CAPTURE_DELAY, delete_old_images, verbose)
recorder.start_recording()
time.sleep(10)
recorder.stop_recording()
```
