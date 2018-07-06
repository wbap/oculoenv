# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import pyglet
import numpy as np

from oculoenv import PointToTargetContent, Environment

content = PointToTargetContent(target_size="small", use_lure=True, lure_size="large")
env = Environment(content)
env.render() # env.window is created here


@env.window.event
def on_key_press(symbol, modifiers):
  from pyglet.window import key

  action = None
  if symbol == key.LEFT:
    print('left')
    action = np.array([0.00, 0.2])
  elif symbol == key.RIGHT:
    print('right')
    action = np.array([0.00, -0.2])
  elif symbol == key.UP:
    print('up')
    action = np.array([0.2, 0.00])
  elif symbol == key.DOWN:
    print('down')
    action = np.array([-0.2, 0.00])
  elif symbol == key.BACKSPACE or symbol == key.SLASH:
    print('RESET')
    action = None
    env.reset()
    env.render()
  elif symbol == key.ESCAPE:
    env.close()
    sys.exit(0)
  else:
    return

  if action is not None:
    obs, reward, done, info = env.step(action)
    print('reward=%d' % (reward))
    env.render()

    if done:
      print('done!')
      env.reset()
      env.render()

pyglet.app.run()

env.close()
