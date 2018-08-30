# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random
from pyglet.gl import *

from .base_content import BaseContent, ContentSprite

PHASE_START = 0
PHASE_FIND = 1

START_MARKER_WIDTH = 0.15  # マーカーの半分の幅 (1.0で画面いっぱい)

BUTTON_WIDTH = 0.1

HIT_NONE = 0
HIT_NO = 1
HIT_YES = 2

DISTRACTION_TYPE_COLOR = 0
DISTRACTION_TYPE_SHAPE = 1
DISTRACTION_TYPE_CONJUNCTION = 2
DISTRACTION_TYPE_MAX = 3

COLORS = [
    [1.0, 0.0, 0.75],  # Magenta, target Color
    [1.0, 0.75, 0.0],
    [0.0, 1.0, 1.0],
    [0.0, 0.25, 1.0],
    [0.5, 0.0, 1.0],
]

GRID_DIVISION = 7
SIGN_SCALE = 0.8

MAX_STEP_COUNT = 180 * 60


class VisualSearchSignSprite(object):
    def __init__(self, textures, tex_index, pos_index, color_index):
        self.tex_index = tex_index
        self.tex = textures[tex_index]
        self.color = COLORS[color_index]
        self.width = (2.0 * 0.8) / (GRID_DIVISION * 2) # half width of this sprite

        x_index = pos_index % GRID_DIVISION
        y_index = pos_index // GRID_DIVISION

        self.pos_x = -self.width * GRID_DIVISION + self.width * (
            1 + 2 * x_index)
        self.pos_y = -self.width * GRID_DIVISION + self.width * (
            1 + 2 * y_index)

        self.is_target = (tex_index == 0 and color_index == 0)

    def render(self, common_quad_vlist):
        glColor3f(*self.color)

        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, 0.0)
        scaled_width = self.width * SIGN_SCALE
        glScalef(scaled_width, scaled_width, scaled_width)
        glBindTexture(self.tex.target, self.tex.id)
        common_quad_vlist.draw(GL_QUADS)
        glPopMatrix()


class VisualSearchContent(BaseContent):
    difficulty_range = 6
    
    def __init__(self, difficulty=None):
        super(VisualSearchContent, self).__init__()
        
        self.difficulty = difficulty
        assert (difficulty is None) or (difficulty < self.difficulty_range)

    def _init(self):
        start_marker_texture = self._load_texture('start_marker0.png')
        white_texture = self._load_texture('white0.png')

        sign_pathes = [
            'general_t0.png', 'general_t1.png', 'general_l0.png',
            'general_l1.png', 'general_r0.png', 'general_r1.png',
            'general_s0.png', 'general_z0.png'
        ]
        self.sign_textures = self._load_textures(sign_pathes)

        self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                          START_MARKER_WIDTH)

        self.button_sprite_no = ContentSprite(
            white_texture, -0.2, -0.9, BUTTON_WIDTH, color=[0.0, 0.0,
                                                            0.0])  # Left
        self.button_sprite_yes = ContentSprite(
            white_texture, 0.2, -0.9, BUTTON_WIDTH, color=[0.0, 0.0,
                                                           0.0])  # Right

        self.reaction_step = 0
        self.phase = PHASE_START

    def _get_sign_variables(self, pos_index, distraction_type, has_target):
        # If target is present, target should be located at the first in the array.
        if has_target and pos_index == 0:
            tex_index = 0
            color_index = 0
        else:
            if distraction_type == DISTRACTION_TYPE_COLOR:
                tex_index = 0
                color_index = np.random.randint(1, len(COLORS))
            elif distraction_type == DISTRACTION_TYPE_SHAPE:
                tex_index = np.random.randint(1, len(self.sign_textures))
                color_index = 0
            else:
                index = np.random.randint(
                    1,
                    len(self.sign_textures) * len(COLORS))
                tex_index = index // len(COLORS)
                color_index = index % len(COLORS)
        return tex_index, color_index

    def _prepare_sign_sprites(self):
        # Choose sign size between 2 and 7.
        if self.difficulty == None:
            sign_size = np.random.randint(low=2, high=2+self.difficulty_range)
        else:
            sign_size = 2 + self.difficulty
        pos_indices = list(range(GRID_DIVISION * GRID_DIVISION))
        random.shuffle(pos_indices)
        pos_indices = pos_indices[:sign_size]
        dice = np.random.randint(2)
        has_target = (dice == 1)

        distraction_type = np.random.randint(DISTRACTION_TYPE_MAX)

        sign_sprites = []

        for i in range(sign_size):
            tex_index, color_index = self._get_sign_variables(
                i, distraction_type, has_target)
            sign_sprite = VisualSearchSignSprite(self.sign_textures, tex_index,
                                                 pos_indices[i], color_index)
            sign_sprites.append(sign_sprite)
        self.sign_sprites = sign_sprites

    def _reset(self):
        self._move_to_start_phase()

    def _is_target_present(self):
        return self.sign_sprites[0].is_target

    def _step(self, local_focus_pos):
        reward = 0

        need_render = False

        info = {}

        if self.phase == PHASE_START:
            if self.start_sprite.contains(local_focus_pos):
                # When hitting the red plus cursor
                self._move_to_find_phase()
                need_render = True
        else:
            self.reaction_step += 1
            hit_type = HIT_NONE

            if self.button_sprite_no.contains(local_focus_pos):
                hit_type = HIT_NO
            elif self.button_sprite_yes.contains(local_focus_pos):
                hit_type = HIT_YES

            if hit_type != HIT_NONE:
                if hit_type == HIT_NO:
                    if not self._is_target_present():
                        # If there is no target and hit NO button
                        reward = 1
                elif hit_type == HIT_YES:
                    if self._is_target_present():
                        # If there is target and hit YES button
                        reward = 1
                if reward == 1:
                    info['result'] = 'success'
                else:
                    info['result'] = 'fail'
                info['reaction_step'] = self.reaction_step
                self._move_to_start_phase()
                need_render = True

        done = self.step_count >= (MAX_STEP_COUNT - 1)
        return reward, done, need_render, info

    def _render(self):
        if self.phase == PHASE_START:
            self.start_sprite.render(self.common_quad_vlist)
        else:
            self.button_sprite_no.render(self.common_quad_vlist)
            self.button_sprite_yes.render(self.common_quad_vlist)

            for sign_sprite in self.sign_sprites:
                sign_sprite.render(self.common_quad_vlist)

    def _move_to_start_phase(self):
        """ Change phase to red plus cursor showing. """
        self.phase = PHASE_START

    def _move_to_find_phase(self):
        """ Change phase to target finding. """
        self._prepare_sign_sprites()
        self.reaction_step = 0
        self.phase = PHASE_FIND
