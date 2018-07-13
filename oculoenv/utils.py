# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import math


def get_subdir_path(sub_dir):
    # Get the directory this module is located in
    abs_path_module = os.path.realpath(__file__)
    module_dir, _ = os.path.split(abs_path_module)

    dir_path = os.path.join(module_dir, sub_dir)

    return dir_path


def get_file_path(sub_dir, file_name):
    """
    Get the absolute path of a resource file, which may be relative to
    the agi_lab module directory, or an absolute path.

    This function is necessary because the simulator may be imported by
    other packages, and we need to be able to load resources no matter
    what the current working directory is.
    """

    # If this is already a real path
    if os.path.exists(file_name):
        return file_name

    subdir_path = get_subdir_path(sub_dir)
    file_path = os.path.join(subdir_path, file_name)

    return file_path


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def rad2deg(radian):
    degree = radian * -180.0 / math.pi
    return degree


def deg2rad(degree):
    radian = degree / 180.0 * math.pi
    return radian
