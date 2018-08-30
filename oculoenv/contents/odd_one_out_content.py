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

MAX_STEP_COUNT = 180 * 60

SIGN_SCALE = 0.8

ODD_TYPE_COLOR = 0
ODD_TYPE_SHAPE = 1
ODD_TYPE_ORIENTATION = 2
ODD_TYPE_MOTION = 3
ODD_TYPE_MAX = 4

COLORS = [
    [1, 0, 0],  # Red
    [1, 1, 0],  # Yellow
    [0, 1, 0],  # Green
    [0, 1, 1],  # Cyan
    [0, 0, 1],  # Blue
    [1, 0, 1]   # Magenta
]

GRID_DIVISIONS = [3, 5, 7]

MOTION_INTERVAL_FRAMES = 2


class OddOneOutSignSprite(object):
    def __init__(self,
                 textures,
                 tex_index,
                 x_index,
                 y_index,
                 grid_division,
                 color_index,
                 has_motion,
                 odd=False):
        self.tex_index = tex_index
        self.tex = textures[tex_index]
        self.color = COLORS[color_index]
        self.width = 2.0 / (grid_division * 2)  # half width of this sprite
        self.base_pos_x = -1.0 + self.width * (1 + 2 * x_index)
        self.base_pos_y = -1.0 + self.width * (1 + 2 * y_index)

        self.has_motion = has_motion
        self.odd = odd
        self.motion_count = 0
        self.motion_pos_index = 0

        if self.has_motion:
            self._set_motion_pos()
        else:
            self._set_random_pos()

    def render(self, common_quad_vlist):
        glColor3f(*self.color)

        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, 0.0)
        scaled_width = self.width * SIGN_SCALE
        glScalef(scaled_width, scaled_width, scaled_width)
        glBindTexture(self.tex.target, self.tex.id)
        common_quad_vlist.draw(GL_QUADS)
        glPopMatrix()

    def _set_random_pos(self):
        dx = np.random.uniform(-1.0, 1.0)
        dy = np.random.uniform(-1.0, 1.0)
        rate = 0.15
        self.pos_x = self.base_pos_x + dx * rate * self.width
        self.pos_y = self.base_pos_y + dy * rate * self.width

    def _set_motion_pos(self):
        dx = 0.0
        dy = 0.0

        if self.motion_pos_index == 0:
            if self.tex_index == 2:  # Horizontal
                dy = -1.0
            else:
                dx = -1.0
        else:
            if self.tex_index == 2:  # Horizontal
                dy = 1.0
            else:
                dx = 1.0

        rate = 0.2
        self.pos_x = self.base_pos_x + dx * self.width * rate
        self.pos_y = self.base_pos_y + dy * self.width * rate

    def step(self):
        """
        Returns:
          Whether need repaint or not.
        """
        if self.has_motion:
            self.motion_count += 1
            if self.motion_count >= MOTION_INTERVAL_FRAMES:
                self.motion_pos_index = 1 - self.motion_pos_index
                self.motion_count = 0
                self._set_motion_pos()
                return True
        return False

    def contains(self, pos):
        """ Retuens whether specified position is inside the sprite rect.
    
        Arguments:
          pos:  Float Array, [X,Y] position
        Returns:
          Boolean, whether position is inside or not.
        """
        px = pos[0]
        py = pos[1]

        scaled_width = self.width * SIGN_SCALE

        return \
          (px >= self.base_pos_x - scaled_width) and \
          (px <= self.base_pos_x + scaled_width) and \
          (py >= self.base_pos_y - scaled_width) and \
          (py <= self.base_pos_y + scaled_width)


class OddOneOutContent(BaseContent):
    difficulty_range = 0
    
    def __init__(self):
        super(OddOneOutContent, self).__init__(bg_color=[0.0, 0.0, 0.0, 1.0])

    def _init(self):
        start_marker_texture = self._load_texture('start_marker0.png')

        self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                          START_MARKER_WIDTH)

        sign_pathes = [
            'general_plus0.png',
            'general_rect0.png',
            'general_h_bar0.png',
            'general_v_bar0.png'
        ]
        self.sign_textures = self._load_textures(sign_pathes)

        self._prepare_sign_sprites()

        self.phase = PHASE_START
        self.reaction_step = 0

    def _prepare_sign_sprites(self):
        odd_type = np.random.randint(0, ODD_TYPE_MAX)

        out = self._get_sign_variables(odd_type)
        main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion = out

        grid_division_index = np.random.randint(0, len(GRID_DIVISIONS))
        grid_division = GRID_DIVISIONS[grid_division_index]

        self.sign_sprites = []

        count = 0
        odd_index = np.random.randint(grid_division * grid_division)

        for i in range(grid_division):
            for j in range(grid_division):
                tex_index = main_tex_index
                color_index = main_color_index
                has_motion = False

                odd = count == odd_index
                if odd:
                    tex_index = odd_tex_index
                    color_index = odd_color_index
                    if has_odd_motion:
                        has_motion = True

                sign_sprite = OddOneOutSignSprite(
                    self.sign_textures,
                    tex_index,
                    i,
                    j,
                    grid_division=grid_division,
                    color_index=color_index,
                    has_motion=has_motion,
                    odd=odd)
                self.sign_sprites.append(sign_sprite)
                count += 1

    def _reset(self):
        self._move_to_start_phase()

    def _check_odd_hit(self, local_focus_pos):
        for sign_sprite in self.sign_sprites:
            if sign_sprite.odd and sign_sprite.contains(local_focus_pos):
                return True
        return False

    def _get_sign_variables(self, odd_type):
        """ Collect variables(color, tex and motion) for applied odd type. """
        main_color_index = 0
        odd_color_index = 0
        main_tex_index = 0
        odd_tex_index = 0
        has_odd_motion = False

        if odd_type == ODD_TYPE_COLOR:
            main_tex_index = np.random.randint(0, 4)  # 0~3
            odd_tex_index = main_tex_index

            color_indices = list(range(len(COLORS)))
            random.shuffle(color_indices)
            main_color_index = color_indices[0]
            odd_color_index = color_indices[1]

        elif odd_type == ODD_TYPE_SHAPE:
            main_tex_index = np.random.randint(0, 2)  # 0 or 1
            odd_tex_index = 1 - main_tex_index
            main_color_index = np.random.randint(0, len(COLORS))
            odd_color_index = main_color_index

        elif odd_type == ODD_TYPE_ORIENTATION:
            main_tex_index = np.random.randint(2, 4)  # 2 or 3
            odd_tex_index = 5 - main_tex_index
            main_color_index = np.random.randint(0, len(COLORS))
            odd_color_index = main_color_index

        elif odd_type == ODD_TYPE_MOTION:
            main_tex_index = np.random.randint(2, 4)  # 2 or 3
            odd_tex_index = main_tex_index
            main_color_index = np.random.randint(0, len(COLORS))
            odd_color_index = main_color_index
            has_odd_motion = True

        return main_tex_index, odd_tex_index, main_color_index, odd_color_index, has_odd_motion

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
            need_render = False

            for sign_sprite in self.sign_sprites:
                need_repaint = sign_sprite.step()
                if need_repaint:
                    need_render = True

            found_odd = self._check_odd_hit(local_focus_pos)
            if found_odd:
                reward = 1
            if reward > 0:
                info = {}
                # This rask's result is always 'success'
                info['result'] = 'success'
                info['reaction_step'] = self.reaction_step
                self._move_to_start_phase()
                need_render = True

        done = self.step_count >= (MAX_STEP_COUNT - 1)
        return reward, done, need_render, info

    def _render(self):
        if self.phase == PHASE_START:
            self.start_sprite.render(self.common_quad_vlist)
        else:
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
