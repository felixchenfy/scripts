

import cv2 
import glob 
import numpy as np 
import sys, os 


src = "/home/feiyu/Downloads/images/downloads/room images/"
dst = "/home/feiyu/Downloads/images/downloads/out/"

# Define functions
def resize(img):
    r0, c0 = img.shape[0:2]
    r_dst = 480
    c_dst = int(c0*r_dst/r0)
    res = cv2.resize(img, (c_dst, r_dst))
    return res 

def get_filenames3(folder, file_types=('*.jpg', '*.png')):
    filenames = []
    for file_type in file_types:
        filenames.extend(glob.glob(folder + "/" + file_type))
    filenames.sort()
    return filenames


# Check input
if not os.path.exists(src):
    raise ValueError('Invalid src folder.')
if not os.path.exists(dst):
    os.makedirs(dst)

# Read image, resize, and then output
format = ".jpg"
src_files = get_filenames3(src)
for i, f in enumerate(src_files):
    img = cv2.imread(f, -1)
    res = resize(img)
    res_name = dst + "{:05d}.jpg".format(i)
    cv2.imwrite(res_name, res)
    print(i)