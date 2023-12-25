'''
Function:
    Given a log folder path, the script reads in the config.yaml and images, and then 
    draws the 3d point cloud and 2d heightmap.

Example of usage:
    python draw_3d_cloud_and_hmap.py --log-folder 1565727031726_getSuctionPrimitives_2 --tote-id 2

Dependencies:
    $ pip install --user open3d-python
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
import open3d
import copy
import os
import sys
import glob
import argparse
import json
import include.lib_point_cloud as lib_cloud


def parse_args():
    ''' Parse input arguments '''

    parser = argparse.ArgumentParser(
        description="Input a log folder, output 3D point cloud.")
    parser.add_argument("-l", "--log-folder", type=str, required=True,
                        help="path to the log folder")
    parser.add_argument("-t", "--tote-id", type=str, required=True,
                        help="tote id")
    args = parser.parse_args()
    return args


def main(args):
    ''' Read from log folder, and draw the 3d point cloud and 2d heightmap. '''

    # Read two rgbd images from the log folder
    frames, tote = read_2_rgbd_frames(
        args.log_folder, tote_id=args.tote_id, resize_ratio=0.5)

    # Create point cloud
    cloud1 = frames[0].create_color_cloud()
    cloud2 = frames[1].create_color_cloud()
    cloud_axis_tote = lib_cloud.create_cloud_of_xyz_axis(
        transform4x4=tote.get_pose(), axis_len=1.0)
    cloud_axis_cam1 = lib_cloud.create_cloud_of_xyz_axis(
        transform4x4=frames[0].cam_pose, axis_len=0.1)
    cloud_axis_cam2 = lib_cloud.create_cloud_of_xyz_axis(
        transform4x4=frames[1].cam_pose, axis_len=0.1)
    cloud = lib_cloud.merge_clouds([cloud1, cloud2])

    # Draw point cloud
    cloud_viz = lib_cloud.merge_clouds(
        [cloud, cloud_axis_tote, cloud_axis_cam1, cloud_axis_cam2])
    open3d.draw_geometries([cloud_viz])

    # Get heightmap
    heightmap_color = project_cloud_to_tote(
        cloud, tote, cloud_type="color",
        voxel_size=0.002, img_w=300, img_h=200)

    heightmap_depth = project_cloud_to_tote(
        cloud, tote, cloud_type="depth",
        voxel_size=0.002, img_w=300, img_h=200)

    show([heightmap_color, heightmap_depth], figsize=(12, 5))

    # Save point cloud
    open3d.write_point_cloud("tmp.pcd", cloud_viz)


def read_2_rgbd_frames(folder_name, tote_id, resize_ratio=0.5):
    ''' Read from the config.json of the standard log folder. '''

    # Output
    rgbd_frames = []

    # Check input
    if folder_name[-1] != '/':
        folder_name += '/'
    tote_id = str(tote_id)

    # From config.json, read sensor info, and then load color/depth images
    filename = folder_name + "config.json"
    with open(filename) as json_file:
        data = json.load(json_file)
        sensors = data["sensor"]
        cnt_sensor = 0
        for sensor_id, sensor in sensors.items():
            if sensor["tote_id"] != tote_id:
                continue  # find sensor that matches with tote_id
            cnt_sensor += 1
            print("Reading cloud {} ...".format(cnt_sensor))
            color_intr = sensor["color_intr"]
            cam_pose = sensor["pose"]  # 2d list
            intrinsics = open3d.camera.PinholeCameraIntrinsic(
                width=color_intr["width"],
                height=color_intr["height"],
                fx=color_intr["fx"],
                fy=color_intr["fy"],
                cx=color_intr["ppx"],
                cy=color_intr["ppy"],
            )
            cam_pose = np.array(cam_pose)

            # Get image names
            affor_name = folder_name + tote_id + \
                "_" + sensor_id + "_affordance.jpg"
            color_name = folder_name + tote_id + "_" + sensor_id + "_color.png"
            depth_name = folder_name + tote_id + \
                "_" + sensor_id + "_aligned_depth.png"
            if not os.path.exists(affor_name) or not os.path.exists(color_name) or not os.path.exists(depth_name):
                raise IOError("File doesn't exist: \n" + color_name + "\n")

            # Convert to class RgbdFrame
            rgbd_frame = RgbdFrame(
                color_name, depth_name, affor_name,
                intrinsics, cam_pose, resize_ratio)
            rgbd_frames += [rgbd_frame]

        if cnt_sensor != 2:
            raise ValueError("Only {} sensor matches tote_id {}. There must be 2 sensors.".format(
                cnt_sensor, tote_id))

        # Read tote position and size
        tote_info = data["tote"][tote_id]
        tote = Tote(
            translation=tote_info["translation"],
            length=tote_info["length"],
            width=tote_info["width"],
            height=tote_info["height"],
        )
    return rgbd_frames, tote


class Tote(object):
    def __init__(self, translation, length, width, height):
        self.translation = np.array(translation)
        self.length = length
        self.width = width
        self.height = height

    def get_pose(self):
        p = self.translation
        T = np.array([
            [1, 0, 0, p[0]],
            [0, 1, 0, p[1]],
            [0, 0, 1, p[2]],
            [0, 0, 0, 1],
        ])
        return T


class RgbdFrame(object):
    ''' A wrapper to store rgb, depth, affordance, and camera info '''

    def __init__(self, color_name, depth_name, affor_name,
                 intrinsics, cam_pose, resize_ratio):

        #  -- Read images
        self.color = cv2.imread(color_name, cv2.IMREAD_UNCHANGED)
        self.depth = cv2.imread(depth_name, cv2.IMREAD_UNCHANGED)
        self.affor = cv2.imread(affor_name, cv2.IMREAD_UNCHANGED)
        self.color = cv2.cvtColor(self.color, cv2.COLOR_BGR2RGB)

        # -- Store params
        self.color_name = color_name
        self.depth_name = depth_name
        self.affor_name = affor_name
        self.intrinsics = intrinsics
        self.cam_pose = cam_pose

        # -- Preprocess
        self._resize_image(ratio=resize_ratio)
        self.depth = self.depth.astype(np.float32) / 10  # unit: mm
        self.affor = self.affor.astype(np.float32) / 255  # 0~1

    def create_color_cloud(self):
        return self._create_cloud(self.color, self.depth)

    def create_affordance_cloud(self):
        return self._create_cloud(self.affor, self.depth)

    def get_camera_intrinsic_matrix(self):
        return self.intrinsics.intrinsic_matrix

    def _create_cloud(self, color, depth):
        rgbd_image = open3d.create_rgbd_image_from_color_and_depth(
            open3d.Image(color),
            open3d.Image(depth),
            convert_rgb_to_intensity=False)
        cloud = open3d.create_point_cloud_from_rgbd_image(
            rgbd_image, self.intrinsics)
        cloud = self._prepreprocess_cloud(cloud)
        return cloud

    def _prepreprocess_cloud(self, cloud):
        # Filter by range
        cloud = lib_cloud.filt_cloud_by_range(cloud, zmin=0, zmax=1.0)
        # Transform
        cloud.transform(self.cam_pose)
        return cloud

    def _resize_image(self, ratio=0.5):
        self.color = cv2.resize(
            self.color, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        self.depth = cv2.resize(
            self.depth, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        self.affor = cv2.resize(
            self.affor, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        self.intrinsics.intrinsic_matrix = ratio * self.intrinsics.intrinsic_matrix


def project_cloud_to_tote(
        cloud, tote, cloud_type,
        voxel_size, img_w, img_h):
    ''' Project 3d point cloud onto 2d image to get the heightmap '''

    # -- Check input
    supported_cloud_types = ["color", "depth", "affordance"]
    if cloud_type not in supported_cloud_types:
        raise ValueError("Cloud type should be: " + str(supported_cloud_types))
    arr_xyz, arr_rgb = lib_cloud.get_cloud_xyzrgb(cloud)
    if cloud_type == "affordance":
        values = arr_rgb[:, 0:1]
    elif cloud_type == "color":
        values = arr_rgb
    elif cloud_type == "depth":
        values = arr_xyz[:, -1:]  # z value
    channels = values.shape[1]

    # -- Init variables
    N = arr_xyz.shape[0]
    w_mid = (img_w-1)/2.0
    h_mid = (img_h-1)/2.0
    if channels == 1:
        heightmap = np.zeros((img_h, img_w), dtype=np.float32)
    else:
        heightmap = np.zeros((img_h, img_w, channels), dtype=np.float32)

    # -- transform all points into the tote coordinate
    T_tote_to_world = np.linalg.inv(tote.get_pose())

    def transform(arr_xyz, T):
        arr_xyz1 = np.hstack([arr_xyz, np.ones((len(arr_xyz), 1))])
        arr_xyz1_transformed = T.dot(arr_xyz1.T).T
        return arr_xyz1_transformed[:, 0:3]
    arr_xyz = transform(arr_xyz, T_tote_to_world)

    # -- Start to project points
    for i in range(N):

        x, y, z = arr_xyz[i]
        value = values[i]

        wi = int(w_mid - y/voxel_size)
        hi = int(h_mid - x/voxel_size)
        if (wi < 0 or wi >= img_w or hi < 0 or hi >= img_h):
            continue
        if channels == 1:  # Retrain the largest
            heightmap[hi, wi] = max(heightmap[hi, wi], value)
        else:  # over-write old data
            heightmap[hi, wi] = value

    return heightmap


def show(imgs, figsize=(6, 10), layout=None, titles=[],
         show_colorbar=False, if_show=True, color_format='RGB', new_fig=True):
    ''' A wrapper for displaying multiple images '''

    def convert(img):
        '''change image color from "BGR" to "RGB" for plt.plot()'''
        if isinstance(img.flat[0], np.float):
            img = (img*255).astype(np.uint8)
        if color_format == 'BGR' and len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    # Check input
    if isinstance(imgs, np.ndarray):
        imgs = [imgs]
    imgs = [convert(img) for img in imgs]

    # Init figure
    if new_fig:
        plt.figure(figsize=figsize)

    # Set subplot size
    N = len(imgs)
    if layout is not None:
        r, c = layout[0], layout[1]
    else:
        if N <= 4:
            r, c = 1, N
        else:
            r, c = N//4+1, 4

    # Plot
    for i in range(N):
        ax = plt.subplot(r, c, i+1)
        plt.imshow(imgs[i])
        if titles:
            ax.set_title(titles[i], fontsize=15)

        if show_colorbar:
            plt.colorbar()

    if if_show:
        plt.show()


if __name__ == "__main__":
    args = parse_args()
    main(args)
