# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import numpy as np


class Matrix4(object):
    def __init__(self, m=None):
        # numpy ndarray stores values in row major order
        if m is None:
            self.m = np.identity(4, dtype=np.float32)
        else:
            self.m = m

    def set_trans(self, v):
        """ Set translation element of the matrix.
        Arguments:
        v: Float array, element size should be 3 or 4.
           if the size is 4, the fourth value should be 1.0
        """
        for i in range(len(v)):
            self.m[i, 3] = v[i]

    def transform(self, v):
        """ Set translation element of the matrix.
        Arguments:
        v: Float array, element size should be 3 or 4.
           if the size is 4, the fourth value should be 1.0
        Returns:
          Float array of length 4. A transformed vector.
        """
        if len(v) == 3:
            v = (v + [1.0])
        return self.m.dot(v)

    def set_rot_x(self, angle):
        """ Set matrix with rotation around x axis.
        Arguments:
          angle: Float, (radian) angle
        """
        s = math.sin(angle)
        c = math.cos(angle)
        mv = [[1.0, 0.0, 0.0, 0.0],
              [0.0,   c,  -s, 0.0],
              [0.0,   s,   c, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
        self.m = np.array(mv, dtype=np.float32)

    def set_rot_y(self, angle):
        """ Set matrix with rotation around y axis.
        Arguments:
          angle: Float, (radian) angle
        """
        s = math.sin(angle)
        c = math.cos(angle)
        mv = [[  c, 0.0,   s, 0.0],
              [0.0, 1.0, 0.0, 0.0],
              [ -s, 0.0,   c, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
        self.m = np.array(mv, dtype=np.float32)

    def set_rot_z(self, angle):
        """ Set matrix with rotation around y axis.
        Arguments:
          angle: Float, (radian) angle
        """
        s = math.sin(angle)
        c = math.cos(angle)
        mv = [[  c,  -s, 0.0, 0.0],
              [  s,   c, 0.0, 0.0],
              [0.0, 0.0, 1.0, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
        self.m = np.array(mv, dtype=np.float32)

    def get_axis(self, axis_index):
        """ Get specified axis of this matrix.
        Arguments:
          axis: Integer, index of axis
        Returns:
          Numpy float ndarray: length 3
        """
        v = []
        for i in range(3):
            v.append(self.m[i, axis_index])
        return np.array(v)

    def invert(self):
        """ Returns inverted matrix.
        Returns:
          Matrix4, inverted matrix
        """
        m_inv = self.m
        m_inv = np.linalg.inv(self.m)
        mat = Matrix4()
        mat.m = m_inv
        return mat

    def mul(self, mat):
        """ Returns multiplied matrix.
        Returns:
          Matrix4, multipied matrix
        """
        m_mul = self.m.dot(mat.m)
        mat = Matrix4()
        mat.m = m_mul
        return mat

    def get_raw_gl(self):
        """ Returns OpenGL compatible (column major) array representation of the matrix.
        Returns:
          Float array
        """
        m_ret = np.transpose(self.m)
        return m_ret.reshape([16])
