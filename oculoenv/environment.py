# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import numpy as np

import pyglet
from pyglet.gl import *
from ctypes import POINTER

from .graphics import MultiSampleFrameBuffer, FrameBuffer
from .objmesh import ObjMesh
from .utils import clamp, rad2deg, deg2rad
from .geom import Matrix4

BG_COLOR = np.array([0.45, 0.82, 1.0, 1.0])
WHITE_COLOR = np.array([1.0, 1.0, 1.0])

# Camera vertical field of view angle (degree)
CAMERA_FOV_Y = 50

# Initial vertical angle of camera (radian)
CAMERA_INITIAL_ANGLE_V = deg2rad(10.0)

# Max vertical angle of camera (radian)
CAMERA_VERTICAL_ANGLE_MAX = deg2rad(45.0)

# Max horizontal angle of camera (radian)
CAMERA_HORIZONTAL_ANGLE_MAX = deg2rad(45.0)
    

PLANE_DISTANCE = 3.0  # Distance to content plane


class PlaneObject(object):
    def __init__(self):
        # TODO: グリッドをもう少し細かく分けて、TextureのSkewが軽減されるかどうか調べる
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

        self.panel_vlist = pyglet.graphics.vertex_list(4, ('v3f', verts),
                                                       ('t2f', texcs))

    def render(self, content):
        content.bind()
        self.panel_vlist.draw(GL_QUADS)


class SceneObject(object):
    """ A class for drawing .obj mesh object with drawing property (pos, scale etc).

    Arguments:
      obj_name: String, file name of wavefront .obj file.
      pos:      Float array, position of the object
      scale:    Float, scale of the object.
      rot:      Float (radian), rotation angle around Y axis.
    """

    def __init__(self, obj_name, pos=[0, 0, 0], scale=1.0, rot=0.0):

        self.mesh = ObjMesh.get(obj_name)
        self.pos = pos
        self.scale = scale
        self.rot = rad2deg(rot)

    def render(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(self.rot, 0, 1, 0)
        self.mesh.render()
        glPopMatrix()


class Camera(object):
    """ 3D camera class. """

    def __init__(self):
        self.reset()

    def _update_mat(self):
        m0 = Matrix4()
        m1 = Matrix4()
        m0.set_rot_x(self.cur_angle_v)
        m1.set_rot_y(self.cur_angle_h)
        self.m = m1.mul(m0)

    def reset(self):
        self.cur_angle_h = 0  # Horizontal
        self.cur_angle_v = CAMERA_INITIAL_ANGLE_V  # Vertical

        self._update_mat()

    def get_forward_vec(self):
        """ Get forward vector
    
        Returns:
          numpy ndarray (float): size=3
        """
        v = self.m.get_axis(2)  # Get z-axis
        return -1.0 * v  # forward direction is minus z-axis of the matrix

    def change_angle(self, d_angle_h, d_angle_v):
        self.cur_angle_h += d_angle_h  # left-right angle
        self.cur_angle_v += d_angle_v  # top-down angle
        
        self.cur_angle_h = clamp(self.cur_angle_h,
                                 -CAMERA_HORIZONTAL_ANGLE_MAX,
                                 CAMERA_HORIZONTAL_ANGLE_MAX)        
        self.cur_angle_v = clamp(self.cur_angle_v, -CAMERA_VERTICAL_ANGLE_MAX,
                                 CAMERA_VERTICAL_ANGLE_MAX)

        self._update_mat()

    def get_inv_mat(self):
        """ Get invererted camera matrix

        Returns:
          numpy ndarray: inverted camera matrix
        """
        m_inv = self.m.invert()
        return m_inv


class Environment(object):
    """ Task Environmenet class. """

    def __init__(self, content, off_buffer_width=128, on_buffer_width=640):
        """ Oculomotor task environment class.

        Arguments:
          content: (Content) object
          off_buffer_width: (int) pixel width and height size of offscreen render buffer.
          on_buffer_width: (int) pixel width and height size of display window.
        """
        
        # Invisible window to render into (shadow OpenGL context)
        self.shadow_window = pyglet.window.Window(
            width=1, height=1, visible=False)

        self.frame_buffer_off = FrameBuffer(off_buffer_width, off_buffer_width)
        self.frame_buffer_on = FrameBuffer(on_buffer_width, on_buffer_width)

        self.camera = Camera()

        # Window for displaying the environment to humans
        self.window = None

        self.content = content
        self.plane = PlaneObject()

        # Add scene objects
        self._init_scene()

        self.reset()

    def _init_scene(self):
        # Create the objects array
        self.objects = []

        obj = SceneObject("frame0", pos=[0.0, 0.0, -PLANE_DISTANCE], scale=2.0)
        self.objects.append(obj)

    def _get_observation(self):
        # Get rendered image
        image = self._render_offscreen()

        # Change upside-down
        image = np.flip(image, 0)
        
        # Current absolute camera angle
        angle = (self.camera.cur_angle_h, self.camera.cur_angle_v)
        
        obs = {
            "screen":image,
            "angle":angle
        }

        return obs

    def reset(self):
        """ Reset environment.
        
        Returns:
          Dictionary
            "screen" numpy ndarray (Rendered Image)
            "angle" (horizontal angle, vertical angle) Absoulte angles of the camera
        """
        
        self.content.reset()
        self.camera.reset()
        return self._get_observation()

    def _calc_local_focus_pos(self, camera_forward_v):
        """ Calculate local coordinate of view focus point on the content panel. """

        tz = -camera_forward_v[2]
        tx = camera_forward_v[0]
        ty = camera_forward_v[1]

        local_x = tx * (PLANE_DISTANCE / tz)
        local_y = ty * (PLANE_DISTANCE / tz)
        return [local_x, local_y]

    def step(self, action):
        """ Execute one environment step. 
        
        Arguments:
          action: Float array, (horizonal delta angle, vertical delta angle) in radian.
        
        Returns:
          obs, reward, done, info
            obs: Dictionary
              "screen" numpy ndarray (Rendered Image)
              "angle" (horizontal angle, vertical angle) Absoulte angles of the camera
            reward: (Float) Reward 
            done: (Bool) Terminate flag
            info: (Dictionary) Response time and trial result information.
        """
        
        d_angle_h = action[0]  # left-right angle
        d_angle_v = action[1]  # top-down angle
        
        self.camera.change_angle(d_angle_h, d_angle_v)

        camera_forward_v = self.camera.get_forward_vec()
        local_focus_pos = self._calc_local_focus_pos(camera_forward_v)
        reward, done, info = self.content.step(local_focus_pos)

        obs = self._get_observation()

        return obs, reward, done, info

    def close(self):
        pass

    def _render_offscreen(self):
        return self._render_sub(self.frame_buffer_off)

    def render(self, mode='human', close=False):
        if close:
            if self.window:
                self.window.close()
            return

        img = self._render_sub(self.frame_buffer_on)
        if mode == 'rgb_array':
            return img

        if self.window is None:
            config = pyglet.gl.Config(double_buffer=False)
            self.window = pyglet.window.Window(
                width=self.frame_buffer_on.width,
                height=self.frame_buffer_on.height,
                resizable=False,
                config=config)

        self.window.clear()
        self.window.switch_to()
        self.window.dispatch_events()

        # Bind the default frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Setup orghogonal projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glOrtho(0, self.frame_buffer_on.width, 0, self.frame_buffer_on.height,
                0, 10)

        # Draw the image to the rendering window
        width = img.shape[1]
        height = img.shape[0]
        img_data = pyglet.image.ImageData(
            width,
            height,
            'RGB',
            img.ctypes.data_as(POINTER(GLubyte)),
            pitch=width * 3,
        )
        img_data.blit(
            0,
            0,
            0,
            width=self.frame_buffer_on.width,
            height=self.frame_buffer_on.height)

        # Force execution of queued commands
        glFlush()

    def _render_sub(self, frame_buffer):
        self.shadow_window.switch_to()

        frame_buffer.bind()

        # Clear the color and depth buffers
        glClearColor(*BG_COLOR)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            CAMERA_FOV_Y,
            frame_buffer.width / float(frame_buffer.height),
            0.04,  # near plane
            100.0  # far plane
        )

        # Apply camera angle
        glMatrixMode(GL_MODELVIEW)
        m = self.camera.get_inv_mat()
        glLoadMatrixf(m.get_raw_gl().ctypes.data_as(POINTER(GLfloat)))

        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # For each object
        glColor3f(*WHITE_COLOR)
        for obj in self.objects:
            obj.render()

        # Draw content panel
        glEnable(GL_TEXTURE_2D)
        glPushMatrix()
        glTranslatef(0.0, 0.0, -PLANE_DISTANCE)
        glScalef(1.0, 1.0, 1.0)
        self.plane.render(self.content)
        glPopMatrix()

        return frame_buffer.read()
