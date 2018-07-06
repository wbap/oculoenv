# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np

from oculoenv.contents.point_to_target_content import Quadrant, PointToTargetContent


class TestQuadrant(unittest.TestCase):
  def test_get_random_location(self):
    margin = 0.1
    # Adding right and bottom margin
    quadrant = Quadrant([0.5, 0.5], 0.5, 0.5-margin, 0.5, 0.5-margin)
    
    for _ in range(100):
      target_width = 0.1
      p = quadrant.get_random_location(target_width)
      # Check x range
      self.assertGreaterEqual(p[0], target_width)
      self.assertLessEqual(p[0], 1.0 - target_width - margin)
      # Check y range
      self.assertGreaterEqual(p[1], target_width + margin)
      self.assertLessEqual(p[1], 1.0 - target_width)


class TestPointToTargetContent(unittest.TestCase):
  def test_plus_target_confolict(self):
    # Check conflict with random location and plus target region
    content = PointToTargetContent(target_size="small", use_lure=False, lure_size="small")

    for i in range(100):
      for j in range(4):
        target_width = 0.1
        pos = content.quadrants[j].get_random_location(target_width)
        x = pos[0]
        y = pos[1]
        # Check whether random location pos is not inside the plus marker
        inside_plus_marker = x > -0.15 and x < 0.15 and y > -0.15 and y < 0.15
        self.assertFalse(inside_plus_marker)


  def test_step_content(self):
    # TODO: Check reacinihg terminal state at max time step
    pass


if __name__ == '__main__':
  unittest.main()
