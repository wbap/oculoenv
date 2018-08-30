# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random

from .base_content import BaseContent, ContentSprite

PHASE_START = 0
PHASE_TARGET = 1

START_MARKER_WIDTH = 0.15  # マーカーの半分の幅 (1.0で画面いっぱい)
TARGET_WIDTH_SMALL = 0.1
TARGET_WIDTH_LARGE = 0.2

MAX_STEP_COUNT = 180 * 60


class Quadrant(object):
    def __init__(self, center, width_left, width_right, width_top,
                 width_bottom):
        self.center = center
        self.width_left = width_left
        self.width_right = width_right
        self.width_top = width_top
        self.width_bottom = width_bottom

    def get_random_location(self, target_width):
        """ Get random location in this quadrant given target size. 
        Arguments:
          target_width: Float, half width of the target
        Returns:
          (Float, Float) Position of the random target location in this quadrant.
        """
        minx = self.center[0] - self.width_left + target_width
        maxx = self.center[0] + self.width_right - target_width
        miny = self.center[1] - self.width_bottom + target_width
        maxy = self.center[1] + self.width_top - target_width

        x = np.random.uniform(low=minx, high=maxx)
        y = np.random.uniform(low=miny, high=maxy)
        return (x, y)


class PointToTargetContent(BaseContent):
    difficulty_range = 3
    
    def __init__(self, difficulty=None):
        self.difficulty = difficulty
        assert (difficulty is None) or (difficulty < self.difficulty_range)
        
        self.quadrants = []
        # To avoid confilict with plus marker, adding margin
        margin = START_MARKER_WIDTH
        self.quadrants.append(
            Quadrant(
                [0.5, 0.5],
                0.5 - margin,
                0.5,  # left margin
                0.5,
                0.5 - margin))  # bottom margin
        self.quadrants.append(
            Quadrant(
                [-0.5, 0.5],
                0.5,
                0.5 - margin,  # right margin
                0.5,
                0.5 - margin))  # bottom margin
        self.quadrants.append(
            Quadrant(
                [-0.5, -0.5],
                0.5,
                0.5 - margin,  # right margin
                0.5 - margin,
                0.5))  # top margin
        self.quadrants.append(
            Quadrant(
                [0.5, -0.5],
                0.5 - margin,
                0.5,  # left margin
                0.5 - margin,
                0.5))  # top margin

        super(PointToTargetContent, self).__init__()

    def _init(self):
        start_marker_texture = self._load_texture('start_marker0.png')
        e_marker_texture = self._load_texture('general_e0.png')

        # (1.0, 1.0)が右上の座標
        self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                          START_MARKER_WIDTH)

        self.target_sprite = ContentSprite(
            e_marker_texture,
            0.0, 0.0, TARGET_WIDTH_SMALL, color=[0.0, 0.0, 0.0])
        self.lure_sprite = ContentSprite(
            e_marker_texture,
            0.0, 0.0, TARGET_WIDTH_SMALL, rot_index=1, color=[0.0, 0.0, 0.0])

        if self.difficulty is not None:
            # If task difficulty is explicitly applied, keep specific target and lure sizes
            # during entire episode. (Otherwise change size 
            self._apply_difficulty(self.difficulty)
            
        self.phase = PHASE_START
        self.reaction_step = 0

    def _reset(self):
        self._move_to_start_phase()

    def _step(self, local_focus_pos):
        reward = 0

        need_render = False

        info = {}

        if self.phase == PHASE_START:
            if self.start_sprite.contains(local_focus_pos):
                # When hitting the red plus cursor
                self._move_to_target_phase()
                need_render = True
        else:
            self.reaction_step += 1
            if self.target_sprite.contains(local_focus_pos):
                # When hitting the target
                reward = 2
                info['result'] = 'success'
                info['reaction_step'] = self.reaction_step
            elif self.lure_sprite.contains(local_focus_pos):
                # When hitting the lure
                reward = 1
                info['result'] = 'fail'
                info['reaction_step'] = self.reaction_step
            if reward > 0:
                self._move_to_start_phase()
                need_render = True

        done = self.step_count >= (MAX_STEP_COUNT - 1)
        return reward, done, need_render, info

    def _render(self):
        if self.phase == PHASE_START:
            self.start_sprite.render(self.common_quad_vlist)
        else:
            self.lure_sprite.render(self.common_quad_vlist)
            self.target_sprite.render(self.common_quad_vlist)

    def _move_to_start_phase(self):
        """ Change phase to red plus cursor showing. """
        self.phase = PHASE_START

    def _apply_difficulty(self, current_difficulty):
        """ Change target and lure size based on the difficulty. """
            
        if current_difficulty == 0:
            # Target is large, lure is small
            self.target_sprite.set_width(TARGET_WIDTH_LARGE)
            self.lure_sprite.set_width(TARGET_WIDTH_SMALL)
        elif current_difficulty == 1:
            # Target is large, lure is large or
            # Target is small, lure is small
            if np.random.randint(0, 2) == 0:
                self.target_sprite.set_width(TARGET_WIDTH_LARGE)
                self.lure_sprite.set_width(TARGET_WIDTH_LARGE)
            else:
                self.target_sprite.set_width(TARGET_WIDTH_SMALL)
                self.lure_sprite.set_width(TARGET_WIDTH_SMALL)
        else:
            # Target is small, lure is large
            self.target_sprite.set_width(TARGET_WIDTH_SMALL)
            self.lure_sprite.set_width(TARGET_WIDTH_LARGE)

    def _locate_targets(self):
        if self.difficulty is None:
            # Change target and lure size randomly.
            current_difficulty = np.random.randint(0, self.difficulty_range)
            self._apply_difficulty(current_difficulty)
        
        indices = list(range(4))
        random.shuffle(indices)

        target_quadrant_index = indices[0]
        target_pos = self.quadrants[target_quadrant_index].get_random_location(
            self.target_sprite.width)
        self.target_sprite.set_pos(target_pos)

        lure_quadrant_index = indices[1]
        lure_pos = self.quadrants[lure_quadrant_index].get_random_location(
            self.lure_sprite.width)
        self.lure_sprite.set_pos(lure_pos)

    def _move_to_target_phase(self):
        """ Change phase to target showing. """
        self._locate_targets()
        self.phase = PHASE_TARGET
        self.reaction_step = 0
