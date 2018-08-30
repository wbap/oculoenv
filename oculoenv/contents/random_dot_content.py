# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import math
from pyglet.gl import *

from .base_content import BaseContent, ContentSprite

PHASE_START = 0
PHASE_RESPONSE = 1

START_MARKER_WIDTH = 0.15  # マーカーの半分の幅 (1.0で画面いっぱい)

MAX_STEP_COUNT = 180 * 60

DOT_NUM = 100
DOT_HALF_WIDTH = 0.02

DOT_SPEED = 0.03

# Gaussian standatd deviation for color attenuation calculation
ATTENUATE_GAUSSIAN_SIGMA_SQ = (0.2 * 0.2)

COHERENT_RATES = [0.7, 0.5, 0.3, 0.1, 0.05]

ARROW_DISTANCE = 0.8
ARROW_HALF_WIDTH = 0.08

ARROW_HIT_NONE = 0
ARROW_HIT_INCORRECT = 1
ARROW_HIT_CORRECT = 2

DOT_MOVE_RANGE = 0.6


class DotSprite(object):
    def __init__(self, tex):
        self.tex = tex
        self.color = [1,1,1]

        self.is_coherent = True
        
        self._set_random_pos()
        self._update_color()

    def render(self, common_quad_vlist, index):
        glColor3f(*self.color)

        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, -5 + 0.01 * index)
        glScalef(DOT_HALF_WIDTH, DOT_HALF_WIDTH, DOT_HALF_WIDTH)
        glBindTexture(self.tex.target, self.tex.id)
        common_quad_vlist.draw(GL_QUADS)
        glPopMatrix()

    def _set_random_pos(self):
        x = np.random.uniform(-DOT_MOVE_RANGE, DOT_MOVE_RANGE)
        y = np.random.uniform(-DOT_MOVE_RANGE, DOT_MOVE_RANGE)
        self.pos_x = x
        self.pos_y = y

    def _update_color(self):
        d = math.sqrt(self.pos_x * self.pos_x + self.pos_y * self.pos_y)
        rate = (1.0 / np.sqrt(2*np.pi*ATTENUATE_GAUSSIAN_SIGMA_SQ)) * np.exp(-(d**2)/(2*ATTENUATE_GAUSSIAN_SIGMA_SQ))
        rate = rate * 1.1
        self.color = [rate,rate,rate]
        
    def step(self, dx, dy):
        if self.is_coherent:
            self.pos_x += dx
            self.pos_y += dy
            if self.pos_x > DOT_MOVE_RANGE: self.pos_x -= (DOT_MOVE_RANGE * 2.0)
            if self.pos_x < -DOT_MOVE_RANGE: self.pos_x += (DOT_MOVE_RANGE * 2.0)
            if self.pos_y > DOT_MOVE_RANGE: self.pos_y -= (DOT_MOVE_RANGE * 2.0)
            if self.pos_y < -DOT_MOVE_RANGE: self.pos_y += (DOT_MOVE_RANGE * 2.0)
        else:
            self._set_random_pos()
        self._update_color()

    

class RandomDotMotionDiscriminationContent(BaseContent):
    difficulty_range = len(COHERENT_RATES)
    
    def __init__(self, difficulty=None):
        super(RandomDotMotionDiscriminationContent, self).__init__(bg_color=[0.0, 0.0, 0.0, 1.0])
        
        self.difficulty = difficulty
        assert (difficulty is None) or (difficulty < self.difficulty_range)

    def _init(self):
        start_marker_texture = self._load_texture('start_marker0.png')
        
        self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                          START_MARKER_WIDTH)
        
        dot_texture = self._load_texture('dot0.png')
        
        self.dot_sprites = []
        for _ in range(DOT_NUM):
            dot_sprite = DotSprite(dot_texture)
            self.dot_sprites.append(dot_sprite)

        self._prepare_arrow_sprites()
        
        self.phase = PHASE_START
        self.reaction_step = 0
        self.current_direction_index = 0

    def _reset(self):
        self._move_to_start_phase()

    def _step(self, local_focus_pos):
        reward = 0

        need_render = False

        info = {}

        if self.phase == PHASE_START:
            if self.start_sprite.contains(local_focus_pos):
                # When hitting the red plus cursor
                self._move_to_response_phase()
                need_render = True
        else:
            # Response phase
            need_render = True
            self.reaction_step += 1

            direction = math.pi / 4.0 * self.current_direction_index
            dx = math.cos(direction) * DOT_SPEED
            dy = math.sin(direction) * DOT_SPEED

            for dot_sprite in self.dot_sprites:
                dot_sprite.step(dx, dy)
            hit = self._check_arrow_hit(local_focus_pos)

            if hit == ARROW_HIT_CORRECT:
                reward = 1
                info['result'] = 'success'
            elif hit == ARROW_HIT_INCORRECT:
                reward = 0
                info['result'] = 'fail'
            if hit == ARROW_HIT_CORRECT or hit == ARROW_HIT_INCORRECT:
                info['reaction_step'] = self.reaction_step
                self._move_to_start_phase()
                need_render = True

        done = self.step_count >= (MAX_STEP_COUNT - 1)
        return reward, done, need_render, info

    def _render(self):
        if self.phase == PHASE_START:
            self.start_sprite.render(self.common_quad_vlist)
        else:
            for i,dot_sprite in enumerate(self.dot_sprites):
                dot_sprite.render(self.common_quad_vlist, i)
            for arrow_sprite in self.arrow_sprites:
                arrow_sprite.render(self.common_quad_vlist)

    def _check_arrow_hit(self, local_focus_pos):
        for i,arrow_sprite in enumerate(self.arrow_sprites):
            if arrow_sprite.contains(local_focus_pos):
                if self.current_direction_index == i:
                    return ARROW_HIT_CORRECT
                else:
                    return ARROW_HIT_INCORRECT
        return ARROW_HIT_NONE
    
    def _move_to_start_phase(self):
        """ Change phase to red plus cursor showing. """
        self.phase = PHASE_START

    def _move_to_response_phase(self):
        """ Change phase to respond. """
        # Randomize direction
        self.current_direction_index = np.random.randint(0, 8)
        
        # Choose coherent rate
        if self.difficulty == None:        
            coherent_rate_index = np.random.randint(0, len(COHERENT_RATES))
        else:
            coherent_rate_index = self.difficulty
        coherent_rate = COHERENT_RATES[coherent_rate_index]
        coherent_dot_num = int(DOT_NUM * coherent_rate)

        for i,dot_sprite in enumerate(self.dot_sprites):
            is_coherent = i < coherent_dot_num
            # Set dot coherent flag
            dot_sprite.is_coherent = is_coherent

        self.reaction_step = 0
        # Change phase
        self.phase = PHASE_RESPONSE


    def _prepare_arrow_sprites(self):
        arrow_texture0 = self._load_texture('arrow0.png')
        arrow_texture1 = self._load_texture('arrow1.png')

        self.arrow_sprites = []
        
        for i in range(8):
            direction = math.pi / 4.0 * i
            x = math.cos(direction) * ARROW_DISTANCE
            y = math.sin(direction) * ARROW_DISTANCE

            if i % 2 == 0:
                tex = arrow_texture0
            else:
                tex = arrow_texture1
            rot_index = i // 2
            
            arrow_sprite = ContentSprite(tex, x, y,
                                         ARROW_HALF_WIDTH,
                                         rot_index=rot_index)
            self.arrow_sprites.append(arrow_sprite)
