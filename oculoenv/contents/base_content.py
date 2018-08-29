# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

import pyglet
from pyglet.gl import *
from ctypes import POINTER

from ..graphics import MultiSampleFrameBuffer, FrameBuffer, load_texture
from ..geom import Matrix4
from ..graphics import load_texture
from ..utils import get_file_path

WHITE_COLOR = np.array([1.0, 1.0, 1.0])


class ContentSprite(object):
    """ A sprite object class that is located in the content panel.
    Currently only square shape is supported.

    Arguments:
      tex:    Texture object
      pos_x:  Float, X position
      pos_y:  Float, Y position
      width:  Float, half width the sprite
      rot_index: Integer, rotation angle index (0=0 degree, 1=90 degree, 2=180 degree, etc...)
      color:  Float Array[3], color for the texture
    """

    def __init__(self,
                 tex,
                 pos_x=0.0,
                 pos_y=0.0,
                 width=1.0,
                 rot_index=0,
                 color=[1.0, 1.0, 1.0]):
        self.tex = tex
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.rot_index = rot_index
        self.color = color

    def render(self, common_quad_vlist):
        glColor3f(*self.color)

        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, 0.0)
        glScalef(self.width, self.width, self.width)
        glRotatef(self.rot_index * 90.0, 0.0, 0.0, 1.0)
        glBindTexture(self.tex.target, self.tex.id)
        common_quad_vlist.draw(GL_QUADS)
        glPopMatrix()

    def set_pos(self, pos):
        self.pos_x = pos[0]
        self.pos_y = pos[1]

    def set_width(self, width):
        self.width = width

    def contains(self, pos):
        """ Retuens whether specified position is inside the sprite rect.
    
        Arguments:
          pos:  Float Array, [X,Y] position
        Returns:
          Boolean, whether position is inside or not.
        """
        px = pos[0]
        py = pos[1]

        return \
          (px >= self.pos_x - self.width) and \
          (px <= self.pos_x + self.width) and \
          (py >= self.pos_y - self.width) and \
          (py <= self.pos_y + self.width)


class BaseContent(object):
    def __init__(self, bg_color=[1.0, 1.0, 1.0, 1.0], width=512, height=512):
        self.bg_color = np.array(bg_color)
        self.width = width
        self.height = height

        self.shadow_window = pyglet.window.Window(
            width=1, height=1, visible=False)

        self.frame_buffer_off = FrameBuffer(width, height)

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

        self.common_quad_vlist = pyglet.graphics.vertex_list(
            4, ('v3f', verts), ('t2f', texcs))
        self._init()
        self.reset()

    def _load_texture(self, file_name):
        path = get_file_path('data/textures', file_name)
        return load_texture(path)

    def _load_textures(self, file_names):
        textures = []

        for file_name in file_names:
            path = get_file_path('data/textures', file_name)
            texture = load_texture(path)
            textures.append(texture)

        return textures

    def reset(self):
        self._reset()
        self.step_count = 0
        # Update offscreen image
        self.render()

    def step(self, local_focus_pos):
        reward, done, need_render, info = self._step(local_focus_pos)
        self.step_count += 1
        if need_render:
            # Update offscreen image
            self.render()
        return reward, done, info

    def render(self):
        """ Render content into offscreen frame buffer texture. """

        # Switch to the default context
        # This is necessary on Linux nvidia drivers
        self.shadow_window.switch_to()

        # Bind the frame buffer
        self.frame_buffer_off.bind()

        # Clear the color and depth buffers
        glClearColor(*self.bg_color)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(-1.0, 1.0, -1.0, 1.0, -10, 10)

        # Set camera rotation and translatoin
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glColor3f(*WHITE_COLOR)

        # Enable alpha blend
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._render()

        # Disable alpha blend
        glDisable(GL_BLEND)

        # TODO: 最終的にマルチサンプルを使わないことにすればこのblitは消える
        self.frame_buffer_off.blit()

        glFlush()

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.frame_buffer_off.tex)

    def _init(self):
        raise NotImplementedError()

    def _reset(self):
        raise NotImplementedError()

    def _step(self, local_focus_pos):
        raise NotImplementedError()
        reward = 0
        done = False
        need_render = True
        return reward, done, need_render

    def _render(self):
        raise NotImplementedError()
