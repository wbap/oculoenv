# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random
from pyglet.gl import *

from .base_content import BaseContent, ContentSprite
from ..graphics import load_texture
from ..utils import get_file_path


PHASE_START = 0
PHASE_FIND = 1

START_MARKER_WIDTH = 0.15 # マーカーの半分の幅 (1.0で画面いっぱい)

MAX_STEP_COUNT = 180 * 60

SIGN_SCALE = 0.8

colors = [[1, 0, 0], # Red
          [1, 1, 0], # Yellow
          [0, 1, 0], # Green
          [0, 1, 1], # Cyan
          [0, 0, 1], # Blue
          [1, 0, 1]] # Magenta


class SignSprite(object):
  def __init__(self, tex, x_index=0, y_index=0, grid_division=3, color_index=0, odd=False):
    self.tex = tex
    self.color = colors[color_index]
    self.width = 2.0 / (grid_division * 2) # half width of this sprite
    self.base_pos_x = -1.0 + self.width * (1 + 2 * x_index)
    self.base_pos_y = -1.0 + self.width * (1 + 2 * y_index)

    self.pos_x = self.base_pos_x
    self.pos_y = self.base_pos_y

    self.odd = odd

  def render(self, common_quad_vlist):
    glColor3f(*self.color)
    
    glPushMatrix()
    glTranslatef(self.pos_x, self.pos_y, 0.0)
    scaled_width = self.width * SIGN_SCALE
    glScalef(scaled_width, scaled_width, scaled_width)
    glBindTexture(self.tex.target, self.tex.id)
    common_quad_vlist.draw(GL_QUADS)
    glPopMatrix()

  def contains(self, pos):
    """ Retuens whether specified position is inside the sprite rect.
    
    Arguments:
      pos:  Float Array, [X,Y] position
    Returns:
      Boolean, whether position is inside or not.
    """
    px = pos[0]
    py = pos[1]
    
    scaled_width = self.width * SIGN_SCALE
    
    return \
      (px >= self.base_pos_x - scaled_width) and \
      (px <= self.base_pos_x + scaled_width) and \
      (py >= self.base_pos_y - scaled_width) and \
      (py <= self.base_pos_y + scaled_width)


class OddOneOutContent(BaseContent):
  def __init__(self):
    super(OddOneOutContent, self).__init__(bg_color=[0.0, 0.0, 0.0, 1.0])


  def _init(self):
    start_marker_path = get_file_path('data/textures', 'start_marker0.png')
    start_marker_texture = load_texture(start_marker_path)
    
    self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                      START_MARKER_WIDTH)
    
    general_sign_path0 = get_file_path('data/textures', 'general_plus0.png')
    general_sign_path1 = get_file_path('data/textures', 'general_rect0.png')
    general_sign_path2 = get_file_path('data/textures', 'general_h_bar0.png')
    general_sign_path3 = get_file_path('data/textures', 'general_v_bar0.png')

    sign_pathes = [general_sign_path0, general_sign_path1,
                   general_sign_path2, general_sign_path3]
    self.sign_textures = [load_texture(path) for path in sign_pathes]

    self._prepare_sign_sprites()

    self.phase = PHASE_START    


  def _prepare_sign_sprites(self):
    grid_division = 3
    self.sign_sprites = []

    count = 0
    odd_index = np.random.randint(grid_division * grid_division)
    
    for i in range(grid_division):
      for j in range(grid_division):
        tex = self.sign_textures[0]
        odd = count == odd_index
        color_index = 0
        if odd:
          color_index = 1
        sign_sprite = SignSprite(tex, i, j, grid_division, color_index=color_index, odd=odd)
        self.sign_sprites.append(sign_sprite)
        count += 1
    
  def _reset(self):
    pass


  def _check_odd_hit(self, local_focus_pos):
    for sign_sprite in self.sign_sprites:
      if sign_sprite.odd and sign_sprite.contains(local_focus_pos):
        return True
    return False
  
  
  def _step(self, local_focus_pos):
    reward = 0

    need_render = False

    if self.phase == PHASE_START:
      if self.start_sprite.contains(local_focus_pos):
        # When hitting the red plus cursor
        self._move_to_find_phase()
        need_render = True
    else:
      # TODO: 毎回強制的に描画更新している
      need_render = True
      
      found_odd = self._check_odd_hit(local_focus_pos)
      if found_odd:
        reward = 1
      if reward > 0:
        self._move_to_start_phase()
    
    done = self.step_count >= (MAX_STEP_COUNT-1)
    return reward, done, need_render


  def _render(self):
    if self.phase == PHASE_START:
      self.start_sprite.render(self.common_quad_vlist)
    else:
      for sign_sprite in self.sign_sprites:
        sign_sprite.render(self.common_quad_vlist)


  def _move_to_start_phase(self):
    """ Change phase to red plus cursor showing. """
    self.phase = PHASE_START

    
  def _move_to_find_phase(self):
    """ Change phase to target showing. """
    self._prepare_sign_sprites()
    self.phase = PHASE_FIND
