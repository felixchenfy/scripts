import cv2
import numpy as np
import glob
import os
from datetime import datetime
import time
import io
import yaml
import types
from shutil import copyfile


def check_and_get_basename(path):
    #   e.g.1: XXX/YYY/ZZZ.avi --> ZZZ
    #   e.g.2: XXX/YYY/ --> YYY
    #   e.g.3: XXX/YYY --> YYY
    if not (os.path.isdir(path) or os.path.exists(path)):
        raise ValueError, "The input data source doesn't exist: " + path
    if not path:
        return ""
    if path[-1] == "/":
        path = path[:-1]
    basename = ("/" + path).split('/')[-1]
    if "." in basename:  # a file
        basename = basename.split('.')[0]
    return basename


def timestamp_to_datetime(timestamp, hour_offset=-4, has_blank=True, has_ms=False):

    ts = float(timestamp)
    ts += hour_offset * 3600  # Boston is in UTC -4 ???

    if has_ms:
        ms = "%.3f" % timestamp
        ms = ms.split('.')[-1]
    else:
        ms = ""

    # if you encounter a "year is out of range" error the timestamp
    # may be in milliseconds, try `ts /= 1000` in that case
    if has_blank:
        res = (datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        if has_ms:
            res += ":" + ms
    else:
        res = (datetime.utcfromtimestamp(ts).strftime('%Y%m%d%H%M%S'))
        if has_ms:
            res += ms
    res = res[2:]  # change 2019xxx to 19xxx
    return res


def get_readable_time(has_blank=False, has_ms=True):
    timestamp = time.time()
    readable_time = timestamp_to_datetime(
        timestamp, has_blank=has_blank, has_ms=has_ms)
    return readable_time


def array_1d_to_2d(arr, row_size):
    if not arr:
        return arr
    return [arr[i:i+row_size] for i in xrange(0, len(arr), row_size)]

# IO ----------------------------------------------------------------


def create_folder(folder):
    if not os.path.exists(folder):
        print("Creating folder:", folder)
        os.makedirs(folder)


def load_yaml(filename):
    with open(filename, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded


def write_list(filename, arr):
    ''' Write list[] to file. Each element takes one row. '''
    create_folder(os.path.dirname(filename))
    with open(file=filename, mode='w') as f:
        for s in arr:
            s = s if isinstance(s, str) else str(s)  # to string
            f.write(s + "\n")


def write_listlist(filename, arrarr):
    ''' Write list[list[]] to file. Each inner list[] takes one row. 
    This is for write yolo labels of each image
    '''
    create_folder(os.path.dirname(filename))
    with open(filename, 'w') as f:
        for j, line in enumerate(arrarr):
            line = [v if isinstance(v, str) else str(v) for v in line]
            for i, val in enumerate(line):
                if i > 0:
                    f.write(" ")
                f.write(val)
            f.write("\n")


def copy_files(src_filenames, dst_folder):
    os.makedirs(dst_folder, exist_ok=True)
    for name_with_path in src_filenames:
        basename = os.path.basename(name_with_path)
        copyfile(src=name_with_path, dst=dst_folder + "/" + basename)

# String/Math/List/Dict ----------------------------------------------------------------


def split_name(name):
    # "/usr/lib/image.jpg" --> ["/usr/lib", "image", ".jpg"]
    pre, ext = os.path.splitext(name)
    if "/" in pre:
        p = pre.rindex('/')
        path = pre[:p]
        name = pre[p+1:]
    else:
        path = "./"
        name = pre
    return path, name, ext


def get_filenames(folder, file_types=('*.jpg', '*.png')):
    filenames = []
    for file_type in file_types:
        filenames.extend(glob.glob(folder + "/" + file_type))
    filenames.sort()
    return filenames


class SimpleNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def dict2class(args_dict):
    args = SimpleNamespace()
    args.__dict__.update(**args_dict)
    return args

# Others ----------------------------------------------------------------


class Timer(object):
    def __init__(self):
        self.t0 = time.time()

    def report_time(self, str_msg):
        t = time.time() - self.t0
        t = "{:.2f}".format(t)
        print("'{}' takes {} seconds".format(str_msg, t))

    def report_time_and_reset(self, str_msg):
        self.report_time(str_msg)
        self.reset()

    def reset(self):
        self.t0 = time.time()


if __name__ == "__main__":
    for i in range(1000):
        res = get_readable_time(has_blank=False, has_ms=True)
        print res
        time.sleep(1)
        # print(time.time())
