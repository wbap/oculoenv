# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np
import math

from oculoenv.contents.random_dot_content import RandomDotMotionDiscriminationContent,\
    PHASE_START, PHASE_RESPONSE, ARROW_HIT_NONE, ARROW_HIT_INCORRECT, ARROW_HIT_CORRECT


class TestRandomDotMotionDiscriminationContent(unittest.TestCase):
    """
    def test_peformance_check(self):
        import time
        
        content = RandomDotMotionDiscriminationContent()

        for i in range(100):
            x = 0
            y = 0
            local_focus_pos = [x, y]
            start = time.time()
            reward, done = content.step(local_focus_pos)
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    """

    def test_reset(self):
        content = RandomDotMotionDiscriminationContent()
        content.reset()
        self.assertEqual(content.phase, PHASE_START)

    def test_check_arrow_hit(self):
        content = RandomDotMotionDiscriminationContent()
        content.current_direction_index = 0

        # Check focus pos and hit results
        hit_correct = content._check_arrow_hit((0.8, 0.0))
        self.assertEqual(hit_correct, ARROW_HIT_CORRECT)

        hit_incorrect = content._check_arrow_hit((-0.8, 0.0))
        self.assertEqual(hit_incorrect, ARROW_HIT_INCORRECT)

        hit_none = content._check_arrow_hit((0.0, 0.0))
        self.assertEqual(hit_none, ARROW_HIT_NONE)

    def test_move_to_start_phase(self):
        content = RandomDotMotionDiscriminationContent()
        content._move_to_start_phase()
        
        self.assertEqual(content.phase, PHASE_START)

    def test_move_to_response_phase(self):
        content = RandomDotMotionDiscriminationContent()
        content._move_to_response_phase()
        
        self.assertEqual(content.phase, PHASE_RESPONSE)
        self.assertTrue(0 <= content.current_direction_index < 8)

    def test_step(self):
        content = RandomDotMotionDiscriminationContent()

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
        self.assertEqual(RandomDotMotionDiscriminationContent.difficulty_range, 5)
        content = RandomDotMotionDiscriminationContent(difficulty=0)

        step_size = 10
        for i in range(step_size):
            x = np.random.uniform(low=-1.0, high=1.0)
            y = np.random.uniform(low=-1.0, high=1.0)
            local_focus_pos = [x, y]
            reward, done, info = content.step(local_focus_pos)

if __name__ == '__main__':
    unittest.main()
