# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import numpy as np
import math

from oculoenv.contents.multiple_object_tracking_content import MultipleObjectTrackingContent, BALL_WIDTH, MOVE_REGION_RATE


class TestMultipleObjectTrackingContent(unittest.TestCase):
    def check_ball_conflict(self, ball_sprites):
        dist_min_sq = (BALL_WIDTH*2) * (BALL_WIDTH*2)
        
        for i,ball_sprite in enumerate(ball_sprites):
            x0 = ball_sprite.pos_x
            y0 = ball_sprite.pos_y

            other_ball_sprites = ball_sprites[0:i]
            for j,other_ball_sprite in enumerate(other_ball_sprites):
                x1 = other_ball_sprite.pos_x
                y1 = other_ball_sprite.pos_y
                dx = x1 - x0
                dy = y1 - y0
                dist_sq = dx*dx + dy*dy
                if dist_sq < dist_min_sq:
                    print("i={}: x={},y={}, j={}:ox={},oy={}".format(i,x0,y0,j,x1,y1))
                    print("dsq={}, dmsq={}".format(dist_sq, dist_min_sq))
                    print("d={}, dm={}".format(math.sqrt(dist_sq), math.sqrt(dist_min_sq)))
                self.assertGreaterEqual(dist_sq, dist_min_sq)

    def check_ball_inside_wall(self, ball_sprites):
        min_pos = -1.0 * MOVE_REGION_RATE
        max_pos = 1.0 * MOVE_REGION_RATE
        
        for ball_sprite in ball_sprites:
            x = ball_sprite.pos_x
            y = ball_sprite.pos_y
            self.assertTrue( x >= min_pos and x <= max_pos or y >= min_pos and y <= max_pos )

    
    def test_move_ball_sprites(self):
        np.random.seed(1)
        
        content = MultipleObjectTrackingContent()

        for i in range(10):
            content._prepare_ball_sprites()
            
            for k in range(100):
                content._move_ball_sprites()
                # Check ball vs ball conflict
                self.check_ball_conflict(content.ball_sprites)
                # Check ball is not outside of the walls
                self.check_ball_inside_wall(content.ball_sprites)

    def test_step(self):
        content = MultipleObjectTrackingContent()

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
        self.assertEqual(MultipleObjectTrackingContent.difficulty_range, 6)
        content = MultipleObjectTrackingContent(difficulty=0)

        step_size = 10
        for i in range(step_size):
            x = np.random.uniform(low=-1.0, high=1.0)
            y = np.random.uniform(low=-1.0, high=1.0)
            local_focus_pos = [x, y]
            reward, done, info = content.step(local_focus_pos)


if __name__ == '__main__':
    unittest.main()
