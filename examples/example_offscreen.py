# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from skimage import io
from oculoenv import PointToTargetContent, Environment

def save_numpy_img(file_name, img):
    img = np.ascontiguousarray(img)
    io.imsave(file_name, img)

lastImgNo = 0

def save_img(img):
    global lastImgNo
    save_numpy_img('out_%03d.png' % lastImgNo, img)
    lastImgNo += 1


def check_offscreen():
    content = PointToTargetContent()
    env = Environment(content)

    frame_size = 10

    for i in range(frame_size):
        dh = np.random.uniform(low=-0.02, high=0.02)
        dv = np.random.uniform(low=-0.02, high=0.02)
        action = np.array([dh, dv])
        obs, reward, done, info = env.step(action)

        image = obs['screen']

        save_img(image)

        if done:
            print("Episode terminated")
            obs = env.reset()


check_offscreen()
