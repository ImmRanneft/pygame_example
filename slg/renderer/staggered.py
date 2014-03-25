__author__ = 'den'

import pygame.rect


class Staggered(object):

    def __init__(self):
        pass

    def map_to_screen(self, drawable):
        [x, y] = drawable.get_coordinates()
        [current_width, current_height] = drawable.get_dimensions()
        [regular_width, regular_height] = drawable.get_regular_tile_dimensions()
        [offset_x, offset_y] = drawable.get_offset()
        tile_x = regular_width * x + int(y) % 2 * regular_width/2

        divider = (current_height - 2 * offset_y) / regular_height * 2
        tile_y = current_height / divider * y
        dy = current_height - regular_height - offset_y + offset_y * y
        tile_y -= dy
        newrect = pygame.rect.Rect((tile_x, tile_y), (drawable.rect.width, drawable.rect.height))

        return newrect

    def draw_map(self, dimensions, container, image):
        for j in range(0, dimensions[1]):
            for i in range(0, dimensions[0]):
                try:
                    tile = container[i][j]
                    if tile and tile.get_id() > 0:
                        tile_rect = self.map_to_screen(tile)
                        image.blit(tile.image, tile_rect)
                except IndexError:
                    print(i, j)
                    exit()