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
  content = PointToTargetContent(target_size="small", use_lure=True, lure_size="large")
  env = Environment(content)

  frame_size = 60 * 180 * 2

  for i in range(frame_size):
    dx = np.random.uniform(low=-0.02, high=0.02)
    dy = np.random.uniform(low=-0.02, high=0.02)
    action = np.array([dx, dy])
    obs, reward, done, info = env.step(action)
    
    if i < 100:
      save_img(obs)
      
    if done:
      print("Episode terminated")
      obs = env.reset()


check_offscreen()
