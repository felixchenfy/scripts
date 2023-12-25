
import cv2
import numpy as np
import glob
import sys
import os
import yaml


def get_filenames(folder, filename_only=False):
    fnames = glob.glob(folder + "/*")
    if filename_only:
        fnames = [s.split("/")[-1] for s in fnames]
    fnames = sorted(fnames)
    return fnames


def makedirs(folders):
    ''' Create directory for all input folders'''
    if isinstance(folders, str):
        folder = folders
        if not os.path.exists(folder):
            os.makedirs(folder)
    elif isinstance(folders, tuple) or isinstance(folders, list):
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
    else:
        raise ValueError, "Wrong folder type: " + folders


def load_config(filepath):
    ''' Load a yaml file and return a dict'''
    with open(filepath, 'r') as f:
        configs = yaml.safe_load(f)
        return configs
    raise ValueError, "Wrong config file"


def read_image(folder, img_index):
    filename = folder + "/{:06d}".format(img_index) + ".png"
    return cv2.imread(filename, cv2.IMREAD_UNCHANGED)


def read_rgbd_image(folder, img_index, is_in_sub_folder=True):
    ''' Read depth and color images. '''
    def read_one_type_of_image(folder, img_index, img_type):
        ''' Helper function to read a color or a depth image.
            if is_in_sub_folder:
                video_path = ${folder}/${img_type}/${img_idex}_${img_type}.png
            else:
                video_path = ${folder}/${img_idex}_${img_type}.png

        Arguments:
            folder {str}
            img_index {int}
            img_tye {str}
        '''
        if is_in_sub_folder:
            folder = folder + "/" + img_type + "/"
        else:
            folder = folder + "/"
        filename = "{:06d}".format(img_index) + "_" + img_type + ".png"
        video_path = folder + filename

        return cv2.imread(video_path, cv2.IMREAD_UNCHANGED)

    color = read_one_type_of_image(folder, img_index, "color")
    depth = read_one_type_of_image(folder, img_index, "depth")
    return color, depth


class VideoWriter(object):
    def __init__(self, video_path, framerate, save_a_sample_per_dt=2.0):

        # -- Settings
        self.video_path = video_path
        self.framerate = framerate
        self.save_a_sample_per_image = int(
            1.0 * save_a_sample_per_dt * framerate)

        # -- Variables
        self.cnt_img = 0
        # initialize later when the 1st image comes
        self.video_writer = None
        self.width = None
        self.height = None

        # -- Create output folder
        folder = os.path.dirname(video_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
            video_path

    def write(self, img):
        self.cnt_img += 1
        if self.cnt_img == 1:  # initialize the video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # define the codec
            self.width = img.shape[1]
            self.height = img.shape[0]
            self.video_writer = cv2.VideoWriter(
                self.video_path, fourcc, self.framerate, (self.width, self.height))
        self.video_writer.write(img)

        if self.cnt_img % self.save_a_sample_per_image == 0:
            filename = os.path.dirname(self.video_path) + "/sample.png"
            cv2.imwrite(filename, img)

    def __del__(self):
        if self.cnt_img > 0:
            self.video_writer.release()
            print "Complete writing video: ", self.video_path

# class ImageWriter(object): # TODO
#     def __init__(self):
#         timestamp = str(time.time()).replace('.', '')

#         self.raw_folder = timestamp + "/"
#         os.makedirs(self.raw_folder)

#         self.result_folder = timestamp + "_res" + "/"
#         os.makedirs(self.result_folder)

#     def save(self, color_img, img_index, img_result=None):

#         filename = "{:06d}".format(img_index) + ".png"

#         # Save raw color_img
#         filepath = self.raw_folder + filename
#         cv2.imwrite(filepath, color_img)

#         # Save result image
#         if img_result is not None:
#             filepath = self.result_folder + filename
#             cv2.imwrite(filename, color_img)

#         if img_result is not None:
#             print "Write raw and result images to: " + filepath
#         else:
#             print "Write raw image to: " + filepath
