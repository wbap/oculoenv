# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np

from oculoenv.contents.odd_one_out_content import OddOneOutSignSprite, OddOneOutContent, \
  ODD_TYPE_COLOR, ODD_TYPE_SHAPE, ODD_TYPE_ORIENTATION, ODD_TYPE_MOTION


class TestOddOneOutSignSprite(unittest.TestCase):
    def test_step(self):
        dummy_textures = [None] * 4
        grid_division = 3

        sign_sprite = OddOneOutSignSprite(
            dummy_textures,
            0,
            0,
            0,
            grid_division=grid_division,
            color_index=0,
            has_motion=True,
            odd=True)
        for i in range(8):
            need_rapaint = sign_sprite.step()
            if i % 4 == 3:
                # Repaint becomes True with every 4 frames
                self.assertTrue(need_rapaint)
            else:
                self.assertFalse(need_rapaint)

    def test_contains(self):
        dummy_textures = [None] * 4
        grid_division = 3

        sign_sprite = OddOneOutSignSprite(
            dummy_textures,
            0,
            1,
            1,  # Will be located at (0,0)
            grid_division=grid_division,
            color_index=0,
            has_motion=True,
            odd=True)

        width = 2.0 / 6.0  # Half width of rectangle

        self.assertTrue(sign_sprite.contains([0, 0]))  # Inside
        self.assertTrue(sign_sprite.contains([width * 0.75, 0]))  # Inside
        self.assertFalse(sign_sprite.contains([width, 0]))  # Outside

        self.assertTrue(sign_sprite.contains([0, 0]))  # Inside
        self.assertTrue(sign_sprite.contains([0, width * 0.75]))  # Inside
        self.assertFalse(sign_sprite.contains([0, width]))  # Outside


class TestOddOneOutContent(unittest.TestCase):
    def test_get_sign_variables(self):
        content = OddOneOutContent()

        # Color
        main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion = \
         content._get_sign_variables(ODD_TYPE_COLOR)
        self.assertEqual(main_tex_index, odd_tex_index)
        self.assertNotEqual(main_color_index, odd_color_index)
        self.assertFalse(has_odd_motion)
        self.assertIn(main_tex_index, [0, 1, 2, 3])
        self.assertIn(odd_tex_index, [0, 1, 2, 3])

        # Shape
        main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion = \
         content._get_sign_variables(ODD_TYPE_SHAPE)
        self.assertNotEqual(main_tex_index, odd_tex_index)
        self.assertEqual(main_color_index, odd_color_index)
        self.assertFalse(has_odd_motion)
        self.assertIn(main_tex_index, [0, 1])
        self.assertIn(odd_tex_index, [0, 1])

        # Orientation
        main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion = \
         content._get_sign_variables(ODD_TYPE_ORIENTATION)
        self.assertNotEqual(main_tex_index, odd_tex_index)
        self.assertEqual(main_color_index, odd_color_index)
        self.assertFalse(has_odd_motion)
        self.assertIn(main_tex_index, [2, 3])
        self.assertIn(odd_tex_index, [2, 3])

        # Motion
        main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion = \
         content._get_sign_variables(ODD_TYPE_MOTION)
        self.assertEqual(main_tex_index, odd_tex_index)
        self.assertEqual(main_color_index, odd_color_index)
        self.assertTrue(has_odd_motion)
        self.assertIn(main_tex_index, [2, 3])
        self.assertIn(odd_tex_index, [2, 3])

    def test_step(self):
        content = OddOneOutContent()

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


if __name__ == '__main__':
    unittest.main()
