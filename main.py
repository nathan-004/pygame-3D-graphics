import pygame

from map import Map
from src.render.utils import *
from src.constants import L
from src.render.camera import Camera

from src.render import main_3D, filter_cubes

map = Map.random((10, 10))

window = pygame.display.set_mode((1280, 780)) # (0, 0), pygame.FULLSCREEN
camera = Camera(Point(1,L * 0.5,1), (window.get_width(), window.get_height()))

WALL_TEXTURE = pygame.image.load("assets/mur_texture.jpg")
FLOOR_TEXTURE = pygame.image.load("assets/sol_texture.png")
CEILING_TEXTURE = pygame.image.load("assets/plafond_texture.jpg")

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
    camera.draw_world(window, filter_cubes(camera, map, world))

if __name__ == "__main__":
    main()