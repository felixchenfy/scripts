#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Basic operations on open3d point cloud '''

import numpy as np
import copy
import open3d
import time
import os
import cv2

# -------------- Basic operations --------------


def clear_cloud(cloud):
    cloud.points = open3d.Vector3dVector(np.ndarray((0, 0)))
    cloud.colors = open3d.Vector3dVector(np.ndarray((0, 0)))


def copy_cloud(src, dst):
    dst.points = copy.deepcopy(src.points)
    dst.colors = copy.deepcopy(src.colors)


def get_cloud_xyzrgb(cloud):
    return np.asarray(cloud.points), np.asarray(cloud.colors)


def form_cloud(np_points, np_colors):
    cloud = open3d.PointCloud()
    cloud.points = open3d.Vector3dVector(np_points)
    cloud.colors = open3d.Vector3dVector(np_colors)
    return cloud


def merge_2clouds(cloud1, cloud2, radius_downsample=None, T=None):
    if T is not None:
        cloud1_transed = copy.deepcopy(cloud1)
        cloud1_transed.transform(T)
    else:
        cloud1_transed = copy.deepcopy(cloud1)
    cloud1_points, cloud1_colors = get_cloud_xyzrgb(cloud1_transed)
    cloud2_points, cloud2_colors = get_cloud_xyzrgb(cloud2)

    out_points = np.vstack((cloud1_points, cloud2_points))
    out_colors = np.vstack((cloud1_colors, cloud2_colors))

    result = form_cloud(out_points, out_colors)
    if radius_downsample is not None:
        result = open3d.voxel_down_sample(result, radius_downsample)
    return result


def merge_clouds(clouds, radius_downsample=None):
    list_xyz = []
    list_rgb = []
    for cloud in clouds:
        xyz, rgb = get_cloud_xyzrgb(cloud)
        list_xyz.append(xyz)
        list_rgb.append(rgb)
    res_xyz = np.vstack(list_xyz)
    res_rgb = np.vstack(list_rgb)
    result = form_cloud(res_xyz, res_rgb)
    if radius_downsample is not None:
        result = open3d.voxel_down_sample(result, radius_downsample)
    return result


def resize_cloud_xyz(cloud, scale=1.0):
    cloud_points, cloud_colors = get_cloud_xyzrgb(cloud)
    cloud_points = cloud_points * scale
    new_cloud = form_cloud(cloud_points, cloud_colors)
    return new_cloud


def remove_cloud_mean(cloud):
    cloud_points, cloud_colors = get_cloud_xyzrgb(cloud)
    cloud_points = cloud_points-np.mean(cloud_points, axis=0)
    new_cloud = form_cloud(cloud_points, cloud_colors)
    return new_cloud

# -------------- Display ----------------


def get_cloud_size(cloud):
    return np.asarray(cloud.points).shape[0]


def draw_2clouds(c1, c2, T_applied_to_c1=None):
    c1_tmp = copy.deepcopy(c1)
    if T_applied_to_c1 is not None:
        c1_tmp.transform(T_applied_to_c1)
    open3d.io.draw_geometries([c1_tmp, c2])


def create_cloud_of_xyz_axis(axis_len=1.0, num_points_in_axis=50, transform4x4=[0, 0, 0]):
    color_map = {'r': [1.0, 0.0, 0.0], 'g': [
        0.0, 1.0, 0.0], 'b': [0.0, 0.0, 1.0]}
    xyz_color = ['r', 'g', 'b']
    NUM_AXIS = 3
    data_xyz = np.zeros((num_points_in_axis*NUM_AXIS, NUM_AXIS))
    data_rgb = np.zeros((num_points_in_axis*NUM_AXIS, NUM_AXIS))
    cnt_row = 0
    for axis in range(3):
        color = color_map[xyz_color[axis]]
        for cnt_points in range(1, 1+num_points_in_axis):
            data_xyz[cnt_row, axis] = axis_len*cnt_points/num_points_in_axis
            data_rgb[cnt_row, :] = color
            cnt_row += 1
    cloud_of_xyz_axes = form_cloud(data_xyz, data_rgb)
    cloud_of_xyz_axes.transform(transform4x4)
    return cloud_of_xyz_axes


def draw_cloud_with_coord(
    cloud,
    axis_len=1.0,
    num_points_in_axis=100,
    transform4x4=np.identity(4),
    if_show=False
):
    cloud_of_xyz_axes = create_cloud_of_xyz_axis(
        axis_len, num_points_in_axis, transform4x4)
    cloud_with_axis = merge_2clouds(cloud, cloud_of_xyz_axes)
    if if_show:
        open3d.draw_geometries([cloud_with_axis])
    return cloud_with_axis

# -------------- Filters ----------------


def filt_cloud_by_range(cloud, xmin=None, xmax=None,
                        ymin=None, ymax=None, zmin=None, zmax=None):
    def none2maxnum(val): return +99999.9 if val is None else val
    def none2minnum(val): return -99999.9 if val is None else val
    xmax = none2maxnum(xmax)
    ymax = none2maxnum(ymax)
    zmax = none2maxnum(zmax)
    xmin = none2minnum(xmin)
    ymin = none2minnum(ymin)
    zmin = none2minnum(zmin)
    def criteria(x, y, z): return \
        x >= xmin and x <= xmax and y >= ymin and y <= ymax and z >= zmin and z <= zmax
    return filt_cloud(cloud, criteria)


def filt_cloud(cloud, criteria):
    points, colors = get_cloud_xyzrgb(cloud)
    num_pts = points.shape[0]
    valid_indices = np.zeros(num_pts, np.int)
    cnt_valid = 0
    for i in range(num_pts):
        x, y, z = points[i][0], points[i][1], points[i][2]
        if criteria(x, y, z):
            valid_indices[cnt_valid] = i
            cnt_valid += 1
    return form_cloud(
        points[valid_indices[:cnt_valid], :],
        colors[valid_indices[:cnt_valid], :]
    )
