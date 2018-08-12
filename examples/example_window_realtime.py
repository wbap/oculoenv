# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import pyglet
from pyglet.window import key
import numpy as np
import argparse


from oculoenv import Environment
from oculoenv import PointToTargetContent, ChangeDetectionContent, OddOneOutContent, VisualSearchContent, \
    MultipleObjectTrackingContent, RandomDotMotionDiscriminationContent

class Contents(object):
    POINT_TO_TARGET = 1
    CHANGE_DETECTION = 2
    ODD_ONE_OUT = 3
    VISUAL_SEARCH = 4
    MULTIPLE_OBJECT_TRACKING = 5
    RANDOM_DOT_MOTION_DISCRIMINATION = 6


class KeyHandler(object):
    def __init__(self, env):
        self.env = env
        self.env.window.push_handlers(self.on_key_press, self.on_key_release)
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.esc_pressed = False
        
        pyglet.clock.schedule_interval(self.update, 1.0/60.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.left_pressed = True
        elif symbol == key.RIGHT:
            self.right_pressed = True
        elif symbol == key.UP:
            self.up_pressed = True
        elif symbol == key.DOWN:
            self.down_pressed = True
        elif symbol == key.ESCAPE:
            self.esc_pressed = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.left_pressed = False
        elif symbol == key.RIGHT:
            self.right_pressed = False
        elif symbol == key.UP:
            self.up_pressed = False
        elif symbol == key.DOWN:
            self.down_pressed = False
        elif symbol == key.ESCAPE:
            self.esc_pressed = False        
        

    def update(self, dt):
        dh = 0.0
        dv = 0.0

        delta_angle = 0.02

        if self.left_pressed:
            dh += delta_angle
        if self.right_pressed:
            dh -= delta_angle
        if self.up_pressed:
            dv += delta_angle
        if self.down_pressed:
            dv -= delta_angle
        if self.esc_pressed:
            self.env.close()
            sys.exit(0)
            return
        
        action = np.array([dv, dh])
        obs, reward, done, info = self.env.step(action)
        self.env.render()

        if done:
            print('done!')
            obs = self.env.reset()
            self.env.render()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", help="\n1: Point To Target\n2: Change Detection\n"
                                          + "3: Odd One Out\n4: Visual Search\n"
                                          + "5: Multiple Object Tracking\n"
                                          + "6: Random Dot Motion Descrimination",
                        type=int)

    args = parser.parse_args()

    if not args.content or args.content == Contents.POINT_TO_TARGET:
        content = PointToTargetContent(target_size="small", use_lure=True, lure_size="large")
    elif args.content == Contents.CHANGE_DETECTION:
        content = ChangeDetectionContent(target_number=2, max_learning_count=20, max_interval_count=10)
    elif args.content == Contents.ODD_ONE_OUT:
        content = OddOneOutContent()
    elif args.content == Contents.VISUAL_SEARCH:
        content = VisualSearchContent()
    elif args.content == Contents.MULTIPLE_OBJECT_TRACKING:
        content = MultipleObjectTrackingContent()
    elif args.content == Contents.RANDOM_DOT_MOTION_DISCRIMINATION:
        content = RandomDotMotionDiscriminationContent()
    else:
        print("Unknown argument")
        sys.exit(1)

    env = Environment(content)
    env.render()  # env.window is created here

    handler = KeyHandler(env)

    pyglet.app.run()

    env.close()

