# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np
import math

from oculoenv.geom import Matrix4


class TestMatrix4(unittest.TestCase):
    def check_matrix_near(self, mat0, mat1):
        ret = np.allclose(mat0.m, mat1.m)
        if not ret:
            print(mat0.m)
            print(mat1.m)
        self.assertTrue(ret)

    def test_init(self):
        mat0 = Matrix4()
        m_test = np.identity(4, dtype=np.float32)
        self.assertTrue(np.allclose(mat0.m, m_test))

    def test_init_with_arg(self):
        mat0 = Matrix4()
        mat1 = Matrix4(np.identity(4, dtype=np.float32))
        self.assertTrue(np.allclose(mat0.m, mat1.m))

    def test_invert(self):
        mat0 = Matrix4()

        mat0.set_rot_x(1.0)
        mat0.set_trans([1.0, 2.0, 3.0])

        mat1 = mat0.invert()
        mat2 = mat1.invert()

        self.check_matrix_near(mat2, mat0)

    def test_set_rot_x(self):
        mat0 = Matrix4()
        v0 = [0, 0, 1]  # z-axis

        for i in range(8):
            angle = i * math.pi / 4.0
            mat0.set_rot_x(angle)
            v1 = mat0.transform(v0)
            ret = np.allclose(
                [0.0, math.sin(-angle),
                 math.cos(-angle), 1.0], v1)
            self.assertTrue(ret)

    def test_set_rot_y(self):
        mat0 = Matrix4()
        v0 = [1, 0, 0]  # x-axis

        for i in range(8):
            angle = i * math.pi / 4.0
            mat0.set_rot_y(angle)
            v1 = mat0.transform(v0)
            ret = np.allclose([math.cos(-angle), 0.0,
                               math.sin(-angle), 1.0], v1)
            self.assertTrue(ret)

    def test_set_rot_z(self):
        mat0 = Matrix4()
        v0 = [0, 1, 0]  # y-axis

        for i in range(8):
            angle = i * math.pi / 4.0
            mat0.set_rot_z(angle)
            v1 = mat0.transform(v0)
            ret = np.allclose([math.sin(-angle),
                               math.cos(-angle), 0.0, 1.0], v1)
            self.assertTrue(ret)

    def test_get_axis(self):
        mat0 = Matrix4()
        np.allclose(mat0.get_axis(0), [1, 0, 0])
        np.allclose(mat0.get_axis(1), [0, 1, 0])
        np.allclose(mat0.get_axis(2), [0, 0, 1])

    def test_mul(self):
        mat0 = Matrix4()
        mat1 = Matrix4()
        mat2 = Matrix4()

        angle = 1.0
        mat0.set_rot_x(angle)
        mat1.set_rot_x(2 * angle)
        mat2.set_rot_x(3 * angle)

        mat3 = mat0.mul(mat1)
        self.check_matrix_near(mat2, mat3)

    def test_get_raw_gl(self):
        mat0 = Matrix4()
        mat0.set_trans([100, 200, 300])

        a = mat0.get_raw_gl()
        a_test = np.array(
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 100, 200, 300, 1],
            dtype=np.float32)

        self.assertTrue(np.allclose(a, a_test))


if __name__ == '__main__':
    unittest.main()
