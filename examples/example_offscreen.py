# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pyglet
import numpy as np

from oculoenv import PointToTargetContent, Environment

def save_numpy_img(file_name, img):
  img = np.ascontiguousarray(img)
  img = np.flip(img, 0)

  from skimage import io
  io.imsave(file_name, img)

lastImgNo = 0

def save_img(img):
  global lastImgNo
  save_numpy_img('out_%03d.png' % lastImgNo, img)
  lastImgNo += 1


def check_offscreen():
  content = PointToTargetContent()
  env = Environment(content)

  # 最初の28フレームがcontent画面に空白となってしまう現象
  action = np.array([0.0, 0.0])
  for i in range(28):
    env.step(action)

  frame_size = 100

  for i in range(frame_size):
    action = np.array([0.0, 0.0])
    obs, reward, done, info = env.step(action)
    save_img(obs)


check_offscreen()
