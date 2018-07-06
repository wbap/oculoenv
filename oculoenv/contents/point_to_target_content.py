# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random

from .base_content import BaseContent, ContentSprite
from ..graphics import load_texture
from ..utils import get_file_path


PHASE_START = 0
PHASE_TARGET = 1

PLUS_MARKER_WIDTH = 0.15 # マーカーの半分の幅 (1.0で画面いっぱい)
TARGET_WIDTH_SMALL = 0.1
TARGET_WIDTH_LARGE = 0.2

MAX_STEP_COUNT = 180 * 60


class Quadrant(object):
  def __init__(self, center, width):
    self.center = center
    self.width = width # half width of this quadrant
    
  def get_random_location(self, target_width):
    """ Get random location in this quadrant given target size. 
    Arguments:
      target_width: Float, half width of the target
    Returns:
      (Float, Float) Position of the random target location in this quadrant.
    """
    minx = self.center[0] - self.width + target_width
    maxx = self.center[0] + self.width - target_width
    miny = self.center[1] - self.width + target_width
    maxy = self.center[1] + self.width - target_width
    
    x = np.random.uniform(low=minx, high=maxx)
    y = np.random.uniform(low=miny, high=maxy)
    return (x, y)


class PointToTargetContent(BaseContent):
  def __init__(self, target_size="small", use_lure=False, lure_size="small"):
    self.target_size = target_size
    self.use_lure = use_lure
    self.lure_size = lure_size

    self.quadrants = []
    self.quadrants.append(Quadrant([0.5, 0.5], 0.5))
    self.quadrants.append(Quadrant([-0.5, 0.5], 0.5))
    self.quadrants.append(Quadrant([-0.5, -0.5], 0.5))
    self.quadrants.append(Quadrant([0.5, -0.5], 0.5))
    
    super(PointToTargetContent, self).__init__()


  def init_content(self):
    plus_marker_path = get_file_path('data/textures', 'plus_marker1', 'png')
    plus_marker_texture = load_texture(plus_marker_path)
    
    e_marker_path = get_file_path('data/textures', 'e_marker1', 'png')
    e_marker_texture = load_texture(e_marker_path)
    
    # (1.0, 1.0)が右上の座標
    self.plus_sprite = ContentSprite(plus_marker_texture, 0.0, 0.0,
                                     PLUS_MARKER_WIDTH)
    
    if self.target_size == "small":
      target_with = TARGET_WIDTH_SMALL
    else:
      target_with = TARGET_WIDTH_LARGE
    if self.lure_size == "small":
      lure_width = TARGET_WIDTH_SMALL
    else:
      lure_width = TARGET_WIDTH_LARGE
    
    self.target_sprite = ContentSprite(e_marker_texture, 0.0, 0.0, target_with)
    self.lure_sprite = ContentSprite(e_marker_texture, 0.0, 0.0, lure_width,
                                     rot_index=1)
    self.phase = PHASE_START

    
  def reset_content(self):
    pass


  def step_content(self, local_focus_pos):
    reward = 0

    if self.phase == PHASE_START:
      if self.plus_sprite.contains_pos(local_focus_pos):
        # When hitting the red plus cursor
        print("hit the plus!!")
        self.move_to_target_phase()
    else:
      if self.target_sprite.contains_pos(local_focus_pos):
        # When hitting the target
        print("hit the targete!!")
        reward = 2
      elif (self.use_lure and self.lure_sprite.contains_pos(local_focus_pos)):
        print("hit the lure!!")
        # When hitting the lure
        reward = 1
      if reward > 0:
        self.move_to_start_phase()
    
    done = self.step_count >= MAX_STEP_COUNT
    return reward, done


  def render_content(self):
    if self.phase == PHASE_START:
      self.plus_sprite.render(self.common_quad_vlist)
    else:
      if self.use_lure:
        self.lure_sprite.render(self.common_quad_vlist)
      self.target_sprite.render(self.common_quad_vlist)


  def move_to_start_phase(self):
    """ Change phase to red plus cursor showing. """
    self.phase = PHASE_START

    
  def locate_targets(self):
    indices = list(range(4))
    random.shuffle(indices)
    
    target_quadrant_index = indices[0]
    target_pos = self.quadrants[target_quadrant_index].get_random_location(
      self.target_sprite.width)
    self.target_sprite.set_pos(target_pos)

    if self.use_lure:
      lure_quadrant_index = indices[1]
      lure_pos = self.quadrants[lure_quadrant_index].get_random_location(
        self.lure_sprite.width)
      self.lure_sprite.set_pos(lure_pos)
    
    
    
  def move_to_target_phase(self):
    """ Change phase to target showing. """
    self.locate_targets()
    self.phase = PHASE_TARGET
