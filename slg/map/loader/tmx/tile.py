__author__ = 'Den'


class Tile(object):

    gid = 0
    __tileset = None

    def __init__(self, tile_gid):

        self.gid = int(tile_gid)

    def set_tileset(self, tileset):
        self.__tileset = tileset

    def get_dimensions(self):
        return self.__tileset.get_tile_dimensions()

    def get_offset(self):
        return self.__tileset.get_offset()

    def get_image(self):
        return self.__tileset.get_image(self.gid)

    def get_rect(self):
        return self.__tileset.get_rect(self.gid)

    def get_image_offset(self):
        return self.__tileset.get_image_offsets(self.gid)

    def get_regular_tile_dimensions(self):
        return self.__tileset.get_regular_tile_dimensions()