# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np

from oculoenv.contents.point_to_target_content import Quadrant, PointToTargetContent


class TestQuadrant(unittest.TestCase):
  def test_get_random_location(self):
    quadrant = Quadrant([0.5, 0.5], 0.5)
    
    for _ in range(100):
      target_width = 0.1
      p = quadrant.get_random_location(target_width)
      # Check x range
      self.assertGreaterEqual(p[0], target_width)
      self.assertLessEqual(p[0], 1.0 - target_width)
      # Check y range
      self.assertGreaterEqual(p[1], target_width)
      self.assertLessEqual(p[1], 1.0 - target_width)



if __name__ == '__main__':
  unittest.main()
