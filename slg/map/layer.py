__author__ = 'den'

import pygame
import pygame.sprite
import pygame.rect
import slg.renderer.staggered
from pygame.locals import *


class Layer(pygame.sprite.Sprite):
    """
    Simple layer, that holds all this tiles and determinates which of them have to be drawn depending in visible_area
    @type _name: str
    @type _order: int
    @type image: pygame.SurfaceType
    @type rect: pygame.rect.Rect
    """

    _name = ''

    _order = 0
    _layer = 'bg'

    _visible_area = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}

    _container = [[]]
    _dimensions = pygame.rect.Rect
    image = None
    rect = None

    def __init__(self, *groups):
        super().__init__(*groups)
        self.dirty = 2

    # setters and getters
    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    name = property(get_name, set_name)

    def set_dimensions(self, dimensions, tile_dimensions):
        self._dimensions = dimensions
        layer_width, layer_height = int(dimensions[0]), int(dimensions[1])
        layer_image_dimensions = [int(dimensions[0]*tile_dimensions[0] + tile_dimensions[0]/2),
                                  int((dimensions[1]+1)*tile_dimensions[1]/2)]

        self.image = pygame.Surface(layer_image_dimensions, SRCALPHA | HWSURFACE)
        self.rect = self.image.get_rect()
        self.source_rect = self.image.get_rect()
        self._container = [[None for x in range(0, layer_height)] for x in range(0, layer_width)]

    def get_order(self):
        return self._order

    def set_order(self, order: int):
        self._order = order

    def update(self, camera):
        camera_bounds = camera.get_bounds()
        for key in camera_bounds.keys():
            if self._visible_area[key] != camera_bounds[key]:
                self._visible_area[key] = camera_bounds[key]
                self.dirty = 1
        if self.dirty > 0:
            self._render(camera)

    def _render(self, camera):
        self.rect = pygame.rect.Rect([-x for x in camera.get_dest()], self.image.get_size())

    def draw(self, renderer):
        for j in range(0, self._dimensions[1]):
            for i in range(0, self._dimensions[0]):
                try:
                    tile = self._container[i][j]
                    if tile and tile.get_id() > 0:
                        tile_rect = renderer.map_to_screen(tile)
                        self.image.blit(tile.image, tile_rect)
                except IndexError:
                    print(i, j)
                    exit()

    def append(self, tile, tilex, tiley):
        try:
            self._container[tilex][tiley] = tile
        except IndexError:
            print('append_error:', tilex, tiley)

    def get(self, coordinates = None):
        if coordinates is not None:
            i = coordinates[0]
            j = coordinates[1]
            return self._container[i][j]
        else:
            return self._container

    order = property(get_order, set_order)
