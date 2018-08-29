# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import math
from pyglet.gl import *

from .base_content import BaseContent, ContentSprite

DEBUGGING = False

PHASE_START = 0
PHASE_MEMORY = 1
PHASE_MOVE = 2
PHASE_RESPONSE = 3

START_MARKER_WIDTH = 0.15  # マーカーの半分の幅 (1.0で画面いっぱい)
BALL_WIDTH = 0.1 # Radius of the ball

BUTTON_WIDTH = 0.1

HIT_NONE = 0
HIT_NO = 1
HIT_YES = 2

BALL_MEMORY_COLOR = [0.0, 0.78, 0.0]
BALL_RESPONSE_COLOR = [0.0, 0.0, 0.78]
BALL_COLOR = [0.0, 0.0, 0.0]

MAX_STEP_COUNT = 180 * 60

MEMORY_STEP_COUNT = 30
MOVE_STEP_COUNT = 60

if DEBUGGING:
    MEMORY_STEP_COUNT = 3


# In what percentage of the region, balls can move.
MOVE_REGION_RATE = 0.7

MOVE_SPEED = 0.05

WATCH_DOG_COUNT = 200



class MultipleObjectTrackingSprite(object):
    def __init__(self, texture, is_memory_target, is_response_target):
        self.tex = texture
        self.width = BALL_WIDTH
        
        self.is_memory_target = is_memory_target
        self.is_response_target = is_response_target
        
    def randomize_pos(self):
        rate_x = np.random.uniform(low=0.0, high=1.0)
        rate_y = np.random.uniform(low=0.0, high=1.0)
        
        self.pos_x = (2.0 * rate_x - 1.0) * MOVE_REGION_RATE
        self.pos_y = (2.0 * rate_y - 1.0) * MOVE_REGION_RATE
        
    def randomize_direction(self):
        self.direction = np.random.uniform(low=-1.0, high=1.0) * np.pi

    def render(self, common_quad_vlist, phase, index):
        if phase == PHASE_MEMORY and self.is_memory_target:
            glColor3f(*BALL_MEMORY_COLOR)
        elif phase == PHASE_RESPONSE and self.is_response_target:
            glColor3f(*BALL_RESPONSE_COLOR)
        else:
            glColor3f(*BALL_COLOR)
            
        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, 0.1 * index)
        glScalef(self.width, self.width, self.width)
        glBindTexture(self.tex.target, self.tex.id)
        common_quad_vlist.draw(GL_QUADS)
        glPopMatrix()
        
    def is_correct_target(self):
        return self.is_memory_target and self.is_response_target

    def is_conflict_with(self, other_ball_sprites):
        for other_ball_sprite in other_ball_sprites:
            dx = self.pos_x - other_ball_sprite.pos_x
            dy = self.pos_y - other_ball_sprite.pos_y
            dist_sq = dx*dx + dy*dy
            dist_min = self.width*2
            if dist_sq < (dist_min * dist_min):
                return True
        return False

    def _check_illegal(self, ball_index, all_ball_sprites):
        illegal = False
        
        if self._is_out_of_wall():
            # If hitting the wall
            illegal = True

        for i,other_ball_sprite in enumerate(all_ball_sprites):
            if i == ball_index:
                continue
            dx = self.cand_pos_x - other_ball_sprite.pos_x
            dy = self.cand_pos_y - other_ball_sprite.pos_y
            dist_sq = dx*dx + dy*dy
            dist_min = self.width*2
            if dist_sq < (dist_min * dist_min):
                illegal = True
        return illegal

    def _move_trial(self):
        dx = math.cos(self.direction) * MOVE_SPEED
        dy = math.sin(self.direction) * MOVE_SPEED
        
        # Move to temporal candidate pos
        self.cand_pos_x = self.pos_x + dx
        self.cand_pos_y = self.pos_y + dy
    
    def move(self, ball_index, all_ball_sprites):
        for wd_count in range(WATCH_DOG_COUNT):
            # Move with current direction
            self._move_trial()

            # Check conflict with other sprites
            conflicted = self._check_illegal(ball_index, all_ball_sprites)
            if conflicted:
                if wd_count >= WATCH_DOG_COUNT-1:
                    # When reaching last watchdog count
                    print("warning: watch dog reached: conflict when moving")
                    # This ball doesn't move.
                    return
                else:
                    # Randomize
                    self.randomize_direction()
                    continue
            break
        # Fix position
        self._fix_pos()

    def _is_out_of_wall(self):
        min_pos = -1.0 * MOVE_REGION_RATE
        max_pos = 1.0 * MOVE_REGION_RATE

        # Check whether temporal candidate pos is out of wall
        if self.cand_pos_x < min_pos or self.cand_pos_x > max_pos or \
           self.cand_pos_y < min_pos or self.cand_pos_y > max_pos:
            return True
        else:
            return False

    def _fix_pos(self):
        self.pos_x = self.cand_pos_x
        self.pos_y = self.cand_pos_y
        

class MultipleObjectTrackingContent(BaseContent):
    difficulty_range = 6
    
    def __init__(self, difficulty=None):
        super(MultipleObjectTrackingContent, self).__init__()
        
        self.difficulty = difficulty
        assert (difficulty is None) or (difficulty < self.difficulty_range)

    def _init(self):
        start_marker_texture = self._load_texture('start_marker0.png')
        white_texture = self._load_texture('white0.png')
        self.ball_texture = self._load_texture('general_round0.png')
        
        self.start_sprite = ContentSprite(start_marker_texture, 0.0, 0.0,
                                          START_MARKER_WIDTH)

        self.button_sprite_no = ContentSprite(
            white_texture, -0.2, -0.9, BUTTON_WIDTH, color=[0.0, 0.0,
                                                            0.0])  # Left
        self.button_sprite_yes = ContentSprite(
            white_texture, 0.2, -0.9, BUTTON_WIDTH, color=[0.0, 0.0,
                                                           0.0])  # Right
        
        self.phase = PHASE_START
        self.phase_count = 0

    def _prepare_ball_sprites(self):
        if self.difficulty == None:
            ball_size = np.random.randint(low=2, high=2+self.difficulty_range)
        else:
            ball_size = 2 + self.difficulty

        dice = np.random.randint(2)
        is_target_correct = (dice == 1)

        memory_target_index = 0

        if is_target_correct:
            # When memorized target is the response taret. (Answer should be YES)
            response_target_index = 0
        else:
            # When memorized target is not the response taret. (Answer should be NO)
            response_target_index = np.random.randint(low=1, high=ball_size)
            
        ball_sprites = []

        for i in range(ball_size):
            ball_sprite = MultipleObjectTrackingSprite(self.ball_texture,
                                                       i == memory_target_index,
                                                       i == response_target_index)
            ball_sprites.append(ball_sprite)
        self.ball_sprites = ball_sprites

        for i, ball_sprite in enumerate(self.ball_sprites):
            ball_sprite.randomize_pos()
            ball_sprite.randomize_direction()

            if i > 0:
                for wd_count in range(WATCH_DOG_COUNT):
                    if ball_sprite.is_conflict_with(self.ball_sprites[0:i]):
                        ball_sprite.randomize_pos()
                    else:
                        break
                    if wd_count == WATCH_DOG_COUNT-1:
                        print("warning: watch dog reached: initial position")
        
    def _is_target_correct(self):
        return self.ball_sprites[0].is_correct_target()

    def _move_ball_sprites(self):
        for i, ball_sprite in enumerate(self.ball_sprites):
            # Check conflict with wall and other balls, and then move it.
            ball_sprite.move(i, self.ball_sprites)
            
    def _reset(self):
        self._move_to_start_phase()

    def _step(self, local_focus_pos):
        reward = 0

        need_render = False

        info = {}

        if self.phase == PHASE_START:
            if self.start_sprite.contains(local_focus_pos):
                # When hitting the red plus cursor
                self._move_to_memory_phase()
                need_render = True
        elif self.phase == PHASE_MEMORY:
            # Memorize position
            self.phase_count += 1
            if self.phase_count >= MEMORY_STEP_COUNT:
                self._move_to_move_phase()
                need_render = True
        elif self.phase == PHASE_MOVE:
            # Move balls
            self._move_ball_sprites()
            self.phase_count += 1
            if self.phase_count >= MOVE_STEP_COUNT:
                self._move_to_response_phase()
            need_render = True
        else:
            # Response phase
            hit_type = HIT_NONE
            self.phase_count += 1

            if self.button_sprite_no.contains(local_focus_pos):
                hit_type = HIT_NO
            elif self.button_sprite_yes.contains(local_focus_pos):
                hit_type = HIT_YES

            if hit_type != HIT_NONE:
                
                if hit_type == HIT_NO:
                    if not self._is_target_correct():
                        # If there is no target and hit NO button
                        reward = 1
                elif hit_type == HIT_YES:
                    if self._is_target_correct():
                        # If there is target and hit YES button
                        reward = 1
                info['reaction_step'] = self.phase_count
                if reward == 1:
                    info['result'] = 'success'
                else:
                    info['result'] = 'fail'
                self._move_to_start_phase()
                need_render = True

        done = self.step_count >= (MAX_STEP_COUNT - 1)
        return reward, done, need_render, info

    def _render(self):
        if self.phase == PHASE_START:
            self.start_sprite.render(self.common_quad_vlist)
        else:
            for i, ball_sprite in enumerate(self.ball_sprites):
                ball_sprite.render(self.common_quad_vlist, self.phase, i)
            if self.phase == PHASE_RESPONSE:
                self.button_sprite_no.render(self.common_quad_vlist)
                self.button_sprite_yes.render(self.common_quad_vlist)

    def _move_to_start_phase(self):
        """ Change phase to red plus cursor showing. """
        self.phase = PHASE_START
        self.phase_count = 0

    def _move_to_memory_phase(self):
        """ Change phase to memorize target """
        self._prepare_ball_sprites()
        self.phase = PHASE_MEMORY
        self.phase_count = 0

    def _move_to_move_phase(self):
        """ Change phase to ball moving """
        self.phase = PHASE_MOVE
        self.phase_count = 0

    def _move_to_response_phase(self):
        """ Change phase to response """
        self.phase = PHASE_RESPONSE
        self.phase_count = 0
        
