import pygame
from math import pi

from map import Map
from src.render.utils import *
from src.render.camera import Camera
from src.constants import *

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

def create_torch(pos: Point, rotation_matrix: Callable = None):
    t = Torch(pos)
    if rotation_matrix is not None:
        t.support.transformation(lambda x : rotate_point(x, rotation_matrix))
    return t

def get_torches(map: Map) -> list:
    torches = []

    for y, row in enumerate(map.map):
        for x, room in enumerate(row):
            if random.choice([True, False]):
                continue

            wall = random.choice([True, True])
            side = random.choice([k for k, val in room.walls.items() if val])

            # Position Y dépend de si la torche est sur le mur ou le sol
            torch_y = L / 2 if wall else 0
            
            # Position X, Z et rotation dépendent du côté
            if side == "left":
                torch_pos = Point(x*L, torch_y, y*L + L/2)
                rotation = get_z_rotation_matrix(-pi/4) if wall else None
            elif side == "right":
                torch_pos = Point(x*L + L, torch_y, y*L + L/2)
                rotation = get_z_rotation_matrix(pi/4) if wall else None
            elif side == "top":
                torch_pos = Point(x*L + L/2, torch_y, y*L)
                rotation = get_x_rotation_matrix(pi/4) if wall else None
            else:
                torch_pos = Point(x*L + L/2, torch_y, y*L + L - 0.1)
                rotation = get_x_rotation_matrix(-pi/4) if wall else None

            torches.append(create_torch(torch_pos, rotation))

    return torches

pygame.font.init()

torches = get_torches(map)
sign = Sign.from_text("Ceci EST un TEST puissant", Point(1, 1, 3), support=True)
ennemy = Ennemy(Point(1,0,4), MONSTER_TEXTURE)
world = get_cubes(map) + torches + [sign] + [ennemy]

f = 0
@main_3D(window, camera, map)
def main():
    global f
    player_light = Light(camera.origine, 1, 10, (1, 0.5, 0))
    filtered_world = filter_cubes(camera, map, world + [player_light])
    camera.draw_world(window, filtered_world)
    
    if f % 1 == 0:
        for torch in torches: # + [sign]
            torch.tick()

    f += 1

if __name__ == "__main__":
    main()