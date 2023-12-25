#!/usr/bin/env python

# Commons
import os
import warnings
try:
    import pyrealsense2 as rs
except:
    warnings.warn("import pyrealsense2 failed. It's not found")
import numpy as np
import cv2
import time
import glob
import Queue # for ROS topic subscriber

# ROS (image subscriber)
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class ImagesLoader(object):
    def __init__(self, src_type, src_filepath="", rostopic_name="", framerate=-1, sensor_id=""):

        assert src_type in ["folder", "realsense", "video", "hikcam_rostopic"]

        if src_type == "folder":
            self.loader = ReadFromFolder(src_filepath)

        if src_type == "realsense":
            # The `framerate` is set as 30
            # As long as 30 is not smaller than config["framerate"],
            #   the realsense's streaming speed won't delay the main program.
            # The `rows` and `cols` can be chosed from (480, 640) or (720, 1280).
            self.loader = ReadFromRealsense(
                sensor_id, framerate=30, rows=480, cols=640)

        if src_type == "video":
            self.loader = ReadFromVideo(src_filepath)

        if src_type == "hikcam_rostopic":
            self.loader = ReadFromRosTopic(rostopic_name)

    def read_image(self):
        return self.loader.read_image()

    def stop(self):
        self.loader.stop()


class ReadFromFolder(object):
    def __init__(self, folder_path):
        self.fnames = sorted(glob.glob(folder_path + "/*"))
        self.cnt_imgs = 0
        self.cur_filename = ""

    def read_image(self):
        if self.cnt_imgs < len(self.fnames):
            self.cur_filename = self.fnames[self.cnt_imgs]
            img = cv2.imread(self.cur_filename, cv2.IMREAD_UNCHANGED)
            self.cnt_imgs += 1
            return img
        else:
            return None
        
    def __len__(self):
        return len(self.fnames)
    
    def get_cur_filename(self):
        return self.cur_filename

    def stop(self):
        None

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
    
class ReadFromRealsense(object):
    def __init__(self, sensor_id, framerate, rows, cols):
        print "Start realsense. ",

        self.is_stoped = False
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.sensor_id = sensor_id
        if sensor_id:
            print "ID: " + sensor_id + ". ",
            self.config.enable_device(sensor_id)

        # -- Settigns
        # img_reversed = True  # Whether camera is reversed or not
        # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16,  framerate)
        self.config.enable_stream(
            rs.stream.color, cols, rows, rs.format.bgr8, framerate)

        # -- Start streamimg and get the configuration if found
        self.cfg = self.pipeline.start(self.config)
        print "Success!"

    def read_image(self):
        max_failures = 100
        color = None
        while max_failures > 0:
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            color = np.asanyarray(color_frame.get_data())
            if color is None:
                max_failures -= 1
                continue
            else: # Successfully read an image
                break
        return color

    def stop(self):
        print "Stop realsense with ID: " + self.sensor_id
        self.pipeline.stop()
        self.is_stoped = True

    def __del__(self):
        if not self.is_stoped:
            self.stop()

CV_BRIDGE = CvBridge()
class ReadFromRosTopic(object):
    def __init__(self, rostopic_name):
        self.cv_imgs_queue = Queue.Queue(maxsize=2)
        self.img_subscriber = rospy.Subscriber(rostopic_name,Image, self.callback_img_subscriber)

    def callback_img_subscriber(self, data):
        cv_img = CV_BRIDGE.imgmsg_to_cv2(data, "bgr8")
        if self.cv_imgs_queue.full(): # if queue is full, pop one
            img_to_discard = self.cv_imgs_queue.get(timeout=0.001)
        self.cv_imgs_queue.put(cv_img, timeout=0.001) # push to queue

    def read_image(self):
        cv_img = self.cv_imgs_queue.get(timeout=10.0)
        return cv_img
        
    def stop(self):
        None