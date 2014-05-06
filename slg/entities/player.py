__author__ = "Den"

import os.path
import math

import pygame
import pygame.sprite
import pygame.rect
from pygame.locals import *

import slg.application.camera
import slg.renderer.staggered

from slg.locals import *


class Player(pygame.sprite.Sprite):

    """
    @type: slg.renderer.Renderer
    """
    _camera = _renderer = None

    movement_speed = 0.1  # 0.05
    moving_x = moving_y = 0
    _map_object = None

    DIRECTION_WEST = 0
    DIRECTION_NORTHWEST = 1
    DIRECTION_NORTH = 2
    DIRECTION_NORTHEAST = 3
    DIRECTION_EAST = 4
    DIRECTION_SOUTHEAST = 5
    DIRECTION_SOUTH = 6
    DIRECTION_SOUTHWEST = 7

    directions = {
        K_a + K_s: DIRECTION_WEST,
        K_a: DIRECTION_NORTHWEST,
        K_a + K_w: DIRECTION_NORTH,
        K_w: DIRECTION_NORTHEAST,
        K_w + K_d: DIRECTION_EAST,
        K_d: DIRECTION_SOUTHEAST,
        K_s + K_d: DIRECTION_SOUTH,
        K_s: DIRECTION_SOUTHWEST,
    }

    @staticmethod
    def get_id():
        return 999999

    def __init__(self, *groups):
        super().__init__(*groups)
        self.manager = None
        self.dir = 0
        self.direction = self.DIRECTION_SOUTH
        self.x, self.y = 0, 13
        self.next_x = self.x
        self.next_y = self.y
        self.moving_x_key = 0
        self.moving_y_key = 0

        self.max_animate_step = 10
        self.min_animate_step = 0
        self.animate_step = self.min_animate_step
        self.last_animate_step_time = 0

        self.sprite = image = pygame.image.load(os.path.join(DATA_DIR, 'monsters', 'zombie.png'))
        self.sprite.convert_alpha()
        self.image = pygame.Surface((128, 128), SRCALPHA | HWSURFACE)
        # self.cl = pygame.Surface((32, 64), SRCALPHA | HWSURFACE)
        # self.cl.fill((255, 0, 0, 128))
        # self.image.blit(self.cl, (48, 40))
        self.image.blit(self.sprite, (0, 0), (0, self.direction*128, 128, 128))

        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())
        self.base_rect = pygame.rect.Rect((0, 0), self.image.get_size())

        self._manager = None
        self.z = 0
        self._layer = self.x + self.y + self.z

    def set_manager(self, manager):
        self._manager = manager
        self._camera = self._manager.get_camera()

    def set_map(self, map_object):
        self._map_object = map_object
        self.z = self._map_object.object_layer
        self._layer = self.x + self.y + self.z
        self._map_object.add(self)
        self._map_object.change_layer(self, self._layer)
        self._renderer = self._map_object.get_renderer()

    def render(self):
        renderer = self._map_object.get_renderer()
        self.base_rect = renderer.map_to_screen(self)
        self.rect = renderer.adjust_with_cam(self.base_rect)

    def update(self):
        if self.moving_x != self._camera.MOVEMENT_STOP or self.moving_y != self._camera.MOVEMENT_STOP:
            self.next_x = self.x + self.moving_x * self.movement_speed
            self.next_y = self.y + self.moving_y * self.movement_speed
            if self.can_move():
                self.x = self.next_x
                self.y = self.next_y
                self._layer = self.x + self.y + 3  # same as object layer
                self._map_object.change_layer(self, self._layer)
        self.render()
        self.update_camera()
        self.animate_me()

    def can_move(self):
        # origin diamond size is 32 x 16 so it`s +0.5 both coordinates
        if self.next_x <= 0 or self.next_y <=0:
            return False
        ceil_coordinates = math.ceil(self.next_x), math.ceil(self.next_y)
        floor_coordinates = math.floor(self.next_x+0.5), math.floor(self.next_y+0.5)

        return not(bool(self._map_object.check_collide(ceil_coordinates[0], ceil_coordinates[1])) or bool(self._map_object.check_collide(floor_coordinates[0], floor_coordinates[1])))

    def __repr__(self):
        return self.rect.__repr__() + "\r\n" + \
            self.base_rect.__repr__() + "\r\n" +\
            str(self.x) + ' ' +\
            str(self.y) + " " + \
            str(self._layer) + " " + \
            self.direction

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_p:
                    print(self, self.directions)
                if e.key == K_c:
                    print(self._camera.get_dest(), self.rect.x, self.rect.y)
                if e.key == K_t and (pygame.key.get_mods() & KMOD_ALT) and (pygame.key.get_mods() & KMOD_SHIFT):
                    self.x = 0
                    self.y = 0
                    break
            if self._manager.state != GAME_STATE_PAUSED:
                need_change = False
                if (e.type == KEYDOWN or e.type == KEYUP) and \
                        (e.key == K_a or e.key == K_s or e.key == K_s or e.key == K_w):
                    need_change = False
                if e.type == KEYDOWN:
                    if e.key == K_s:
                        self.set_moving_y(self._camera.MOVEMENT_POSITIVE)
                        if self.moving_x != self._camera.MOVEMENT_STOP:
                            self.moving_x = self._camera.MOVEMENT_STOP
                        if self.moving_y_key != e.key:
                            need_change = True
                        self.moving_y_key = e.key
                    if e.key == K_w:
                        self.set_moving_y(self._camera.MOVEMENT_NEGATIVE)
                        if self.moving_x != self._camera.MOVEMENT_STOP:
                            self.moving_x = self._camera.MOVEMENT_STOP
                        if self.moving_y_key != e.key:
                            need_change = True
                        self.moving_y_key = e.key
                    if e.key == K_d:
                        if self.moving_y != self._camera.MOVEMENT_STOP:
                            self.moving_y = self._camera.MOVEMENT_STOP
                        self.set_moving_x(self._camera.MOVEMENT_POSITIVE)
                        if self.moving_x_key != e.key:
                            need_change = True
                        self.moving_x_key = e.key
                    if e.key == K_a:
                        if self.moving_y != self._camera.MOVEMENT_STOP:
                            self.moving_y = self._camera.MOVEMENT_STOP
                        self.set_moving_x(self._camera.MOVEMENT_NEGATIVE)
                        if self.moving_x_key != e.key:
                            need_change = True
                        self.moving_x_key = e.key
                if e.type == KEYUP:
                    if (e.key == K_w or e.key == K_s) and e.key == self.moving_y_key:
                        self.set_moving_y(self._camera.MOVEMENT_STOP)
                        self.moving_y_key = 0
                        # need_change = True
                    if (e.key == K_a or e.key == K_d) and e.key == self.moving_x_key:
                        self.set_moving_x(self._camera.MOVEMENT_STOP)
                        self.moving_x_key = 0
                if need_change:
                        self.change_direction()

    def change_direction(self):
        self.dir = self.moving_x_key + self.moving_y_key
        self.direction = self.directions.get(self.dir, self.DIRECTION_SOUTH)
        self.animate_me()

    def animate_me(self):
        if self.moving_x != self._camera.MOVEMENT_STOP or self.moving_y != self._camera.MOVEMENT_STOP:
            time = self._manager.get_time()
            if self.min_animate_step < self.animate_step < self.max_animate_step:
                self.animate_step = self.min_animate_step
            if time > self.last_animate_step_time + 500:
                self.last_animate_step_time = time
                self.animate_step += 1
                if self.animate_step > self.max_animate_step:
                    self.animate_step = self.min_animate_step
        else:
            self.animate_step = 0
        self.image.fill((255, 255, 255, 0))
        self.image.blit(self.sprite, (0, 0), (0, self.direction*128, 128, 128))

    def update_camera(self):
        if self.moving_x != self._camera.MOVEMENT_STOP or self.moving_y != self._camera.MOVEMENT_STOP:
            camera_dim = self._camera.get_dimensions()
            edge_offset = (camera_dim[0] + camera_dim[1]) / 20
            if self.rect.left < 0 + edge_offset and (self.moving_y == self._camera.MOVEMENT_POSITIVE
                                                     or self.moving_x == self._camera.MOVEMENT_NEGATIVE):
                self._camera.set_moving_x(self._camera.MOVEMENT_NEGATIVE)
                self._camera.set_movement_speed(self.movement_speed)
                self._camera.update()
            if self.rect.right > camera_dim[0] - edge_offset and (self.moving_y == self._camera.MOVEMENT_NEGATIVE
                                                                  or self.moving_x == self._camera.MOVEMENT_POSITIVE):
                self._camera.set_moving_x(self._camera.MOVEMENT_POSITIVE)
                self._camera.set_movement_speed(self.movement_speed)
                self._camera.update()
            if self.rect.top < 0 + edge_offset and self.moving_y == self._camera.MOVEMENT_NEGATIVE:
                self._camera.set_moving_y(self._camera.MOVEMENT_NEGATIVE)
                self._camera.set_movement_speed(self.movement_speed)
                self._camera.update()
            if self.rect.bottom > camera_dim[1] - edge_offset and self.moving_y == self._camera.MOVEMENT_POSITIVE:
                self._camera.set_moving_y(self._camera.MOVEMENT_POSITIVE)
                self._camera.set_movement_speed(self.movement_speed)
                self._camera.update()

    def get_regular_tile_dimensions(self):
        return self._map_object.get_tile_dimensions()

    def get_dimensions(self):
        return self.image.get_size()

    @staticmethod
    def get_offset():
        return (32, 16)

    def get_coordinates(self):
        x = self.x
        y = self.y
        return [x, y]

    def set_moving_x(self, movement):
        self.moving_x = movement

    def set_moving_y(self, movement):
        self.moving_y = movement
