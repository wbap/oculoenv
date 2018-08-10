# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np
import math

from oculoenv.contents.random_dot_content import RandomDotMotionDiscriminationContent


class TestRandomDotMotionDiscriminationContent(unittest.TestCase):
    """
    def test_peformance_check(self):
        import time
        
        content = RandomDotMotionDiscriminatorContent()

        for i in range(100):
            x = 0
            y = 0
            local_focus_pos = [x, y]
            start = time.time()
            reward, done = content.step(local_focus_pos)
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    """

    def test_step(self):
        content = RandomDotMotionDiscriminatorContent()

        step_size = 180 * 60

        for i in range(step_size):
            x = np.random.uniform(low=-1.0, high=1.0)
            y = np.random.uniform(low=-1.0, high=1.0)
            local_focus_pos = [x, y]
            reward, done = content.step(local_focus_pos)
            self.assertGreaterEqual(reward, 0)
            if i == (step_size - 1):
                # At the last frame, done becomes True
                self.assertTrue(done)
            else:
                # Otherwise done is False
                self.assertFalse(done)


if __name__ == '__main__':
    unittest.main()
