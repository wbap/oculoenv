# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np
import math

from oculoenv.environment import Environment
from oculoenv.contents.point_to_target_content import Quadrant, PointToTargetContent


class TestEnvironment(unittest.TestCase):
    def test_step(self):
        content = PointToTargetContent()
        env = Environment(content)
        
        action = np.array([0.0, 0.0])
        obs, reward, done, info = env.step(action)

        image = obs['screen']
        angle = obs['angle']

        self.assertTrue(type(image) is np.ndarray)
        self.assertEqual(image.shape, (128,128,3))
        self.assertEqual(len(angle), 2)

        self.assertTrue(type(reward) is int)
        self.assertTrue(type(done) is bool)
        
        self.assertTrue(type(info) is dict)

    def test_reset(self):
        content = PointToTargetContent()
        env = Environment(content)
        
        obs = env.reset()

        image = obs['screen']
        angle = obs['angle']

        self.assertTrue(type(image) is np.ndarray)
        self.assertEqual(image.shape, (128,128,3))
        self.assertEqual(len(angle), 2)

        
if __name__ == '__main__':
    unittest.main()
