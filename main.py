import pygame

from map import Map
from src.render.utils import *
from src.constants import *
from src.render.camera import Camera

from src.render import main_3D, filter_cubes

map = Map.random((10, 10))

window = pygame.display.set_mode((1280, 780)) # (0, 0), pygame.FULLSCREEN
camera = Camera(Point(1,L * 0.5,1), (window.get_width(), window.get_height()))

def get_cubes(map: Map) -> list:
    cubes = []
    for y, row in enumerate(map.map):
        for x, room in enumerate(row):
            cubes.append(
                Cube(L, Point(x*L, 0, y*L), texture=[
                        WALL_TEXTURE if room.walls["top"] else None, WALL_TEXTURE if room.walls["bottom"] else None,
                        WALL_TEXTURE if room.walls["left"] else None, WALL_TEXTURE if room.walls["right"] else None,
                        CEILING_TEXTURE, FLOOR_TEXTURE
                    ]))
    return cubes

world = get_cubes(map)

@main_3D(window, camera, map)
def main():
    player_light = Light(camera.origine, 1, 10, (1, 0.5, 0.5))
    filtered_world = filter_cubes(camera, map, world + [player_light] + [Torch(Point(1.0, 0, 1.0))])
    camera.draw_world(window, filtered_world)

if __name__ == "__main__":
    main()