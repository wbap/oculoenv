# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random

from .base_content import BaseContent, ContentSprite
from enum import Enum


PLUS_MARKER_WIDTH = 0.15  # マーカーの半分の幅 (1.0で画面いっぱい)
TARGET_WIDTH_SMALL = 0.1
TARGET_WIDTH_LARGE = 0.2

BUTTON_HALF_WIDTH = 0.1

MAX_STEP_COUNT = 180 * 60

MIN_INTERVAL_COUNT = 0.2 * 60
MAX_INTERVAL_COUNT = 0.4 * 60

LEARNING_COUNT = 0.3 * 60

TARGET_CHANGE_THRESHOLD = 0.6


class Phase(Enum):
    START = 0
    LEARNING = 1
    INTERVAL = 2
    EVALUATION = 3


class TargetColors(Enum):
    MAGENDA = [1.0, 0.0, 0.75]
    ORANGE = [1.0, 0.75, 0.0]
    LIGHT_BLUE = [0.0, 1.0, 1.0]
    BLUE = [0.0, 0.25, 1.0]
    DEEP_PURPLE = [0.5, 0.0, 1.0]


class PartsColor(Enum):
    BLACK = [0.0, 0.0, 0.0]
    WHITE = [1.0, 1.0, 1.0]


class AnswerBoxHit(Enum):
    NONE = 0
    YES = 1
    NO = 2


class Quadrant(object):
    """def __new__(cls):
        self = super.__new__(cls)
        return self"""

    def __init__(self, center, width_left, width_right, width_top, width_bottom):
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


class EightSquareQuadrantWrapper(object):
    side_section = 8
    width = 0.2
    half_width = width/2

    centers_x = [-0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7]
    centers_y = [-0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7]

    def __init__(self):
        self.quadrants = []

        for center_y in self.centers_y:
            for center_x in self.centers_x:
                center = [center_x, center_y]
                quadrant = Quadrant(center,
                                    self.half_width,
                                    self.half_width,
                                    self.half_width,
                                    self.half_width)
                self.quadrants.append(quadrant)

    def get_location(self, i_x, j_y):
        index = j_y * self.side_section + i_x
        return self.quadrants[index].center

    def get_random_location(self, number):
        samples = random.sample(self.quadrants, k=number)
        centers = []
        for sample in samples:
            centers.append(sample.center)
        return centers


class ChangeDetectionContent(BaseContent):
    def __init__(self):
        super(ChangeDetectionContent, self).__init__()
        self.yes_button_pos = [-0.9, 0.0]
        self.no_button_pos = [0.9, 0.0]

    def _init(self):
        self.quadrants = EightSquareQuadrantWrapper()
        start_marker_texture = self._load_texture('start_marker0.png')
        # (1.0, 1.0)が右上の座標
        self.plus_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                         PLUS_MARKER_WIDTH)

        e_marker_texture = self._load_texture('general_e0.png')
        box_texture = self._load_texture('white0.png')

        # TODO: Initial content sprites should be created in another method.
        self.textures = [e_marker_texture, box_texture]

        target_number = np.random.random_integers(2, 4)
        centers = self.quadrants.get_random_location(target_number)
        self.target_sprites = []
        for center in centers:
            tex_index = np.random.random_integers(0, 1)
            texture = self.textures[tex_index]

            color_index = np.random.random_integers(0, len(TargetColors) - 1)
            color = list(TargetColors)[color_index].value

            sprite = ContentSprite(tex=texture,
                                   pos_x=center[0],
                                   pos_y=center[1],
                                   width=self.quadrants.half_width,
                                   color=color)
            self.target_sprites.append(sprite)

        self.answer_state = AnswerButtonState(box_texture)

        self.phase = Phase.START

    def _reset(self):
        pass

    def _step(self, local_focus_pos):
        reward = 0

        need_render = False
        done = self.step_count >= (MAX_STEP_COUNT - 1)
        print('step=%s' % self.step_count)
        print('phase=%s' % self.phase)

        if self.phase == Phase.START:
            if not self.plus_sprite.contains(local_focus_pos):
                return reward, done, need_render

            # When hitting the red plus cursor
            self._go_into_learning_phase()
            need_render = True
        elif self.phase == Phase.LEARNING:
            self.learning_count += 1

            if self.learning_count < LEARNING_COUNT:
                return reward, done, need_render

            self._go_into_interval_phase()
            need_render = True
        elif self.phase == Phase.INTERVAL:
            self.interval_count += 1

            print('interval=%s' % self.interval_count)

            if self.interval_count < MAX_INTERVAL_COUNT:  # TODO: change interval count randomly.
                return reward, done, need_render

            self._go_into_evaluation_phase()
            need_render = True
        elif self.phase == Phase.EVALUATION:
            hit_type = self.answer_state.detect_hit(local_focus_pos)

            if hit_type == AnswerBoxHit.NONE:
                return reward, done, need_render

            reward = self.evaluate_answer(hit_type)
            self._go_into_start_phase()
            need_render = True

        return reward, done, need_render

    def _render(self):
        if self.phase == Phase.START:
            self.plus_sprite.render(self.common_quad_vlist)
            return

        if self.phase == Phase.INTERVAL:
            return

        for sprite in self.target_sprites:  # Phase.LEARNING or Phase.EVALUATION
            sprite.render(self.common_quad_vlist)

        if self.phase == Phase.EVALUATION:
            self.answer_state.render(self.common_quad_vlist)

    def _go_into_start_phase(self):
        """ Change phase to red plus cursor showing. """
        self.phase = Phase.START

    def _go_into_learning_phase(self):
        self.learning_count = 0
        self.phase = Phase.LEARNING

    def _go_into_interval_phase(self):
        self.interval_count = 0
        self.phase = Phase.INTERVAL

    def _go_into_evaluation_phase(self):
        """ Change phase to target showing. """
        self.phase = Phase.EVALUATION

        if np.random.rand() < TARGET_CHANGE_THRESHOLD:
            self.is_changed = False
            return

        self.is_changed = True
        sprite = np.random.choice(self.target_sprites)

        rand_num = np.random.random_integers(0, 2)
        if rand_num == 0:
            self._change_color(sprite)
        elif rand_num == 1:
            self._change_texture(sprite)
        elif rand_num == 2:
            self._change_color(sprite)
            self._change_texture(sprite)

    def _change_color(self, sprite):
        next_color = np.random.choice(TargetColors)
        while next_color.value == sprite.color:
            next_color = np.random.choice(TargetColors)

        sprite.color = next_color.value

    def _change_texture(self, sprite):
        if sprite.tex == self.textures[0]:
            sprite.tex = self.textures[1]
        else:
            sprite.tex = self.textures[0]

    def evaluate_answer(self, hit_type):
        reward = 0
        if hit_type == AnswerBoxHit.YES and self.is_changed:
            reward = 1
        elif hit_type == AnswerBoxHit.NO and not self.is_changed:
            reward = 1

        return reward


class AnswerButtonState(object):
    def __init__(self, texture):
        self.yes_button = YesButton(texture)
        self.no_button = NoButton(texture)

    def detect_hit(self, local_focus_pos):
        if self.yes_button.contains(local_focus_pos):
            return AnswerBoxHit.YES
        elif self.no_button.contains(local_focus_pos):
            return AnswerBoxHit.NO
        else:
            return AnswerBoxHit.NONE

    def render(self, common_quad_vlist):
        self.yes_button.render(common_quad_vlist)
        self.no_button.render(common_quad_vlist)


class AnswerButtonSprite(ContentSprite):
    def __init__(self, texture):
        super(ContentSprite, self).__init__()

        self.tex = texture
        self.width = BUTTON_HALF_WIDTH
        self.rot_index = 0
        self.color = PartsColor.BLACK.value


class YesButton(AnswerButtonSprite):
    def __init__(self, texture):
        super(YesButton, self).__init__(texture)

        self.pos_x = 0.9
        self.pos_y = 0


class NoButton(AnswerButtonSprite):
    def __init__(self, texture):
        super(NoButton, self).__init__(texture)

        self.pos_x = -0.9
        self.pos_y = 0


