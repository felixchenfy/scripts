'''
Use python to convert a video to gif.
See this post:
https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python

Example of usage:
    $ python video2gif.py -h 
    $　python video2gif.py \
        -i "/home/feiyu/Desktop/learn_coding/test_data/short_video.avi" \
        -o "/home/feiyu/Desktop/learn_coding/test_data/short_video.gif"
    $ python video2gif.py \
        -i "/home/feiyu/Desktop/learn_coding/test_data/short_video.avi" \
        -o "/home/feiyu/Desktop/learn_coding/test_data/short_video.gif" \
        --sample_interval 2 \
        --start_time 0.0 \
        --end_time 10.0 \
        --resize_rate 0.5 \
        --output_fps -1
        
Dependency:
    $ sudo apt install gifsicle

Notes:
    Optimize gif: 
    $ gifsicle -i output.gif -O3 --colors 256 -o output_compressed.gif
'''

import os
import numpy as np
import cv2
import imageio
import subprocess
import argparse

# -- Set arguments
parser = argparse.ArgumentParser(description="Convert a video to gif.")
parser.add_argument("-i", "--input_video_path", type=str, required=True)
parser.add_argument("-o", "--output_gif_path", type=str, required=True)
parser.add_argument("-s", "--sample_interval", type=int, required=False,
                    default=1,
                    help="Sample every kth image from video. Default 1.")
parser.add_argument("-t0", "--start_time", type=float, required=False,
                    default=0.0,
                    help="Start time of the video. Default 0.0.")
parser.add_argument("-te", "--end_time", type=float, required=False,
                    default=999.0,
                    help="End time of the video. Default 999.0.")
parser.add_argument("-rr", "--resize_rate", type=float, required=False,
                    default=1.0,
                    help="Resize rate of the video frame. Default 1.0.")
parser.add_argument("-of", "--output_fps", type=int, required=False,
                    default=-1,
                    help="At what fps to write video frames to gif. "
                    "Default -1, which is reset as `video_fps/sample_interval`.")

CURR_PATH = os.path.dirname(os.path.abspath(__file__))

tmp_image_filename = ".tmp.png"
tmp_gif_filename = ".tmp.gif"


# -- Get arguments
args = parser.parse_args()
input_video_path = args.input_video_path
output_gif_path = args.output_gif_path
sample_interval = args.sample_interval
start_time = args.start_time
end_time = args.end_time
resize_rate = args.resize_rate
output_fps = args.output_fps

# --------------------------- Functions ---------------------------


class ReadFromVideo(object):
    def __init__(self, video_path, sample_interval=1):
        ''' A video reader class for reading video frames from video.
        Arguments:
            video_path
            sample_interval {int}: sample every kth image.
        '''
        if not os.path.exists(video_path):
            raise IOError("Video not exist: " + video_path)
        assert isinstance(sample_interval, int) and sample_interval >= 1
        self.cnt_imgs = 0
        self.is_stoped = False
        self.video = cv2.VideoCapture(video_path)
        ret, frame = self.video.read()
        self.next_image = frame
        self.sample_interval = sample_interval
        self.fps = self.get_fps()
        if not self.fps >= 0.0001:
            import warnings
            warnings.warn("Invalid fps of video: {}".format(video_path))

    def has_image(self):
        return self.next_image is not None

    def get_curr_video_time(self):
        return 1.0 / self.fps * self.cnt_imgs

    def read_image(self):
        image = self.next_image
        for i in range(self.sample_interval):
            if self.video.isOpened():
                ret, frame = self.video.read()
                self.next_image = frame
            else:
                self.next_image = None
                break
        self.cnt_imgs += 1
        return image

    def stop(self):
        self.video.release()
        self.is_stoped = True

    def __del__(self):
        if not self.is_stoped:
            self.stop()

    def get_fps(self):

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        # With webcam get(CV_CAP_PROP_FPS) does not work.
        # Let's see for ourselves.

        # Get video properties
        if int(major_ver) < 3:
            fps = self.video.get(cv2.cv.CV_CAP_PROP_FPS)
        else:
            fps = self.video.get(cv2.CAP_PROP_FPS)
        return fps


if __name__ == "__main__":
    video_reader = ReadFromVideo(input_video_path, sample_interval)
    gif_images = []
    cnt = 0
    while video_reader.has_image():
        image = video_reader.read_image()
        video_time = video_reader.get_curr_video_time()
        if video_time >= start_time:
            if video_time <= end_time:
                cnt += 1
                image = cv2.resize(image, dsize=None, fx=resize_rate, fy=resize_rate)
                cv2.imwrite(tmp_image_filename, image)
                print("Reading the {}th image".format(cnt))
                gif_images.append(imageio.imread(tmp_image_filename))
            else:
                break

    # Write images to gif
    if output_fps == -1:
        output_fps = 1.0 * video_reader.fps / sample_interval
    print("\nStart writing images to gif ...")
    imageio.mimsave(tmp_gif_filename, gif_images, duration=1.0/output_fps)
    
    # Compress gif
    print("\nStart compressing gif ...")
    subprocess.call(["gifsicle",
                     "-i", tmp_gif_filename,
                     "-O3",
                     "--colors", "256",
                     "-o", output_gif_path])

    # Delete tmp files
    print("\nClean temporary files ...")
    subprocess.call(["rm", tmp_gif_filename])
    subprocess.call(["rm", tmp_image_filename])

    # Print helper info
    print("\nDone!")
    print("See the result gif at: " + output_gif_path)

    print("\nHelper command: ")
    print("nautilus " + os.path.dirname(output_gif_path))
