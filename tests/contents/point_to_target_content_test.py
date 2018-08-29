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
        quadrant = Quadrant([0.5, 0.5], 0.5, 0.5 - margin, 0.5, 0.5 - margin)

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
        content = PointToTargetContent()

        for i in range(100):
            for j in range(4):
                target_width = 0.1
                pos = content.quadrants[j].get_random_location(target_width)
                x = pos[0]
                y = pos[1]
                # Check whether random location pos is not inside the plus marker
                inside_plus_marker = x > -0.15 and x < 0.15 and y > -0.15 and y < 0.15
                self.assertFalse(inside_plus_marker)

    def test_step(self):
        content = PointToTargetContent()

        step_size = 180 * 60

        for i in range(step_size):
            x = np.random.uniform(low=-1.0, high=1.0)
            y = np.random.uniform(low=-1.0, high=1.0)
            local_focus_pos = [x, y]
            reward, done, info = content.step(local_focus_pos)
            self.assertGreaterEqual(reward, 0)
            if i == (step_size - 1):
                # At the last frame, done becomes True
                self.assertTrue(done)
            else:
                # Otherwise done is False
                self.assertFalse(done)

    def test_explicity_difficulty_setting(self):
        # Set task difficulty explicitly and confirm target and lure size is fixed.
        self.assertEqual(PointToTargetContent.difficulty_range, 3)
        
        content = PointToTargetContent(difficulty=0)
        self.assertEqual(content.target_sprite.width, 0.2)
        self.assertEqual(content.lure_sprite.width, 0.1)
        
if __name__ == '__main__':
    unittest.main()
