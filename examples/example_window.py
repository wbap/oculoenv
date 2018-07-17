# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import pyglet
import numpy as np
import argparse

from oculoenv import Environment
from oculoenv import PointToTargetContent, ChangeDetectionContent, OddOneOutContent, VisualSearchContent, \
    MultipleObjectTrackingContent


class Contents(object):
    POINT_TO_TARGET = 1
    CHANGE_DETECTION = 2
    ODD_ONE_OUT = 3
    VISUAL_SEARCH = 4
    MULTIPLE_OBJECT_TRACKING = 5


class KeyEventListener(object):
    def __init__(self, env):
        self.env = env
        self.env.window.push_handlers(self.on_key_press)

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key

        action = None
        if symbol == key.LEFT:
            print('left')
            action = np.array([0.00, 0.02])
        elif symbol == key.RIGHT:
            print('right')
            action = np.array([0.00, -0.02])
        elif symbol == key.UP:
            print('up')
            action = np.array([0.02, 0.00])
        elif symbol == key.DOWN:
            print('down')
            action = np.array([-0.02, 0.00])
        elif symbol == key.BACKSPACE or symbol == key.SLASH:
            print('RESET')
            action = None
            self.env.reset()
            self.env.render()
        elif symbol == key.ESCAPE:
            self.env.close()
            sys.exit(0)
        else:
            return

        if action is not None:
            obs, reward, done, info = self.env.step(action)
            print('reward=%d' % (reward))
            self.env.render()

            if done:
                print('done!')
                self.env.reset()
                self.env.render()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", help="\n1: Point To Target\n2: Change Detection\n"
                                          + "3: Odd One Out\n4: Visual Search`\n"
                                          + "5: Multiple Object Tracking", type=int)

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
    else:
        print("Unknown argument")
        sys.exit(1)

    env = Environment(content)
    env.render()  # env.window is created here

    listener = KeyEventListener(env)

    pyglet.app.run()

    env.close()
