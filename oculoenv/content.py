# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np

import pyglet
from pyglet.gl import *
from ctypes import POINTER

from .graphics import MultiSampleFrameBuffer, load_texture
from .utils import rad2deg, deg2rad, get_file_path
from .geom import Matrix4

CONTENT_BG_COLOR = np.array([1.0, 1.0, 1.0, 1.0])
WHITE_COLOR = np.array([1.0, 1.0, 1.0])


class ContentSprite(object):
  """ A sprite object class that is located in the content panel.
  Currently only square shape is supported.

  Arguments:
    tex:    Texture object
    pos_x:  Float, X position
    pos_y:  Float, Y position
    scale:  Float, scale
    rot_index: Integer, rotation angle index (0=0 degree, 1=90 degree, 2=180 degree, etc...)
  """
  
  def __init__(self, tex, pos_x=0.0, pos_y=0.0, scale=1.0, rot_index=0):
    self.tex = tex
    self.pos_x = pos_x
    self.pos_y = pos_y    
    self.scale = scale
    self.rot_index = rot_index


  def render(self, common_quad_vlist):
    glPushMatrix()
    glRotatef(self.rot_index * 90.0, 0.0, 0.0, 1.0)
    glTranslatef(self.pos_x, self.pos_y, 0.0)
    glScalef(self.scale, self.scale, self.scale)
    glBindTexture(self.tex.target, self.tex.id)
    common_quad_vlist.draw(GL_QUADS)
    glPopMatrix()


  def set_pos(self, pos_x, pos_y):
    self.pos_x = pos_x
    self.pos_y = pos_y


  def contains_pos(self, px, py):
    """ Retuens whether specified position is inside the sprite rect.
    
    Arguments:
      px:  Float, X position
      py:  Float, Y position
    Returns:
      Boolean, whether position is inside or not.
    """
    return \
      (px >= self.pos_x - self.scale) and \
      (px <= self.pos_x + self.scale) and \
      (py >= self.pos_y - self.scale) and \
      (py <= self.pos_y + self.scale)
  

class Content(object):
  def __init__(self, width=512, height=512):
    self.width = width
    self.height = height
    
    self.shadow_window = pyglet.window.Window(width=1, height=1, visible=False)

    # TODO: ここはマルチサンプルでなくてよいかもしれない
    self.frame_buffer_off = MultiSampleFrameBuffer(width, height, num_samples=4)
    
    # Create the vertex list for the quad
    verts = [
      -1,  1, 0,
      -1, -1, 0,
       1, -1, 0,
       1,  1, 0,
    ]
    texcs = [
      0, 1,
      0, 0,
      1, 0,
      1, 1,
    ]
    
    self.common_quad_vlist = pyglet.graphics.vertex_list(4,
                                                         ('v3f', verts),
                                                         ('t2f', texcs))
    self.init_content()
    self.reset()


  def reset(self):
    self.reset_content()
    self.step_count = 0


  def step(self, local_focus_pos):
    reward, done = self.step_content(local_focus_pos)
    self.step_count += 1
    return reward, done

  
  def render(self):
    # Render content into offscreen frame buffer texture
    
    # Switch to the default context
    # This is necessary on Linux nvidia drivers
    self.shadow_window.switch_to()

    # Bind the multisampled frame buffer
    self.frame_buffer_off.bind()
    
    # Clear the color and depth buffers
    glClearColor(*CONTENT_BG_COLOR)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    # Set the projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(-1.0, 1.0, -1.0, 1.0, -10, 10)

    # Set camera rotation and translatoin
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glEnable(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glColor3f(*WHITE_COLOR)
    
    self.render_content()
    
    self.frame_buffer_off.blit()


  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.frame_buffer_off.tex)


  def init_content(self):
    pass
    
  def reset_content(self):
    pass
  
  def step_content(self, local_focus_pos):
    reward = 0
    done = False
    return reward, done

  def render_content(self):
    pass



class PointToTargetContent(Content):
  def __init__(self):
    super(PointToTargetContent, self).__init__()


  def init_content(self):
    plus_marker_path = get_file_path('data/textures', 'plus_marker1', 'png')
    plus_marker_texture = load_texture(plus_marker_path)
    
    e_marker_path = get_file_path('data/textures', 'e_marker1', 'png')
    e_marker_texture = load_texture(e_marker_path)
    
    self.plus_sprite = ContentSprite(plus_marker_texture, 0.0, 0.0, 0.1, 0)
    self.e_sprite0 = ContentSprite(e_marker_texture, 0.2, 0.2, 0.1, 0)
    self.e_sprite1 = ContentSprite(e_marker_texture, -0.2, -0.2, 0.1, 1)

    
  def reset_content(self):
    pass

  
  def step_content(self, local_focus_pos):
    reward = 0.0
    done = False
    return reward, done

  
  def render_content(self):
    self.plus_sprite.render(self.common_quad_vlist)
    self.e_sprite0.render(self.common_quad_vlist)
    self.e_sprite1.render(self.common_quad_vlist)    
