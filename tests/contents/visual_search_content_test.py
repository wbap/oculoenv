# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np

from oculoenv.contents.visual_search_content import VisualSearchContent, \
  DISTRACTION_TYPE_COLOR, DISTRACTION_TYPE_SHAPE, DISTRACTION_TYPE_CONJUNCTION


class TestVisualSearchContent(unittest.TestCase):
    def test_get_sign_variables(self):
        content = VisualSearchContent()

        # When target is present, first one should be (0,0)
        self.assertEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_COLOR, True),
            (0, 0))
        self.assertEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_SHAPE, True),
            (0, 0))
        self.assertEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_CONJUNCTION, True),
            (0, 0))

        # When target is not present, first one should not be (0,0)
        self.assertNotEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_COLOR, False),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_SHAPE, False),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(0, DISTRACTION_TYPE_CONJUNCTION,
                                        False), (0, 0))

        # Second one should not be (0,0)
        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_COLOR, True),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_SHAPE, True),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_CONJUNCTION, True),
            (0, 0))

        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_COLOR, False),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_SHAPE, False),
            (0, 0))
        self.assertNotEqual(
            content._get_sign_variables(1, DISTRACTION_TYPE_CONJUNCTION,
                                        False), (0, 0))

        # Check only color is changed
        tex_index, color_index = content._get_sign_variables(
            1, DISTRACTION_TYPE_COLOR, True)
        self.assertEqual(tex_index, 0)
        self.assertNotEqual(color_index, 0)

        # Check only texture is changed
        tex_index, color_index = content._get_sign_variables(
            1, DISTRACTION_TYPE_SHAPE, True)
        self.assertNotEqual(tex_index, 0)
        self.assertEqual(color_index, 0)

    def test_step(self):
        content = VisualSearchContent()

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
        # Set task difficulty explicitly
        self.assertEqual(VisualSearchContent.difficulty_range, 6)
        content = VisualSearchContent(difficulty=0)

        step_size = 10
        for i in range(step_size):
            x = np.random.uniform(low=-1.0, high=1.0)
            y = np.random.uniform(low=-1.0, high=1.0)
            local_focus_pos = [x, y]
            reward, done, info = content.step(local_focus_pos)

if __name__ == '__main__':
    unittest.main()
