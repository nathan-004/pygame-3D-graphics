import pygame
pygame.init()

from math import pi
from copy import copy

from map import Map
from src.render.utils import *
from src.render.camera import Camera
from src.constants import *

from src.render import main_3D, filter_cubes
import src.render.frames as frames
from src.render.transitions import fire_transition

import src.interface.buttons as buttons
from src.interface.bars import get_bar

from src.render.utils import Ennemy as EnnemyRender
from src.game.entities import Ennemy

window = pygame.display.set_mode((780, 780)) # (0, 0), pygame.FULLSCREEN

map = Map.random((10, 10))
print(window)
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

torches = [] #get_torches(map)
sign = Sign.from_text("Ceci EST un TEST puissant", Point(1, 1, 3), support=True)
test_obj = Object.from_file("assets/CUBE.obj", Point(2.5, 2.5, 2.5),texture=CUBE_TEXTURES)
ennemy_render = EnnemyRender(Point(1,0,4), BAT_TEXTURE, camera)
world = get_cubes(map) + torches + [sign] + [ennemy_render] # [test_obj]

fight_monster = EnnemyRender(Point(L*1, -2, L*3), MONSTER_TEXTURE, camera)
ennemy_test = Object.from_file("assets/TEST.obj", Point(L*1, -2, L*3), texture=TEST_TEXTURE)
print(len(ennemy_test.faces))
fight_monster.tick()
fight_monster.face.transformation(lambda x: x * 4)
fight_monster_entity = Ennemy('Vilain Test', 100, 1, 0.1, fight_monster)

fight_room = Cuboid(
    L*4, L*4, L*4, Point(0, 0, 0), 
    texture=[WALL_TEXTURE, WALL_TEXTURE, WALL_TEXTURE, WALL_TEXTURE, CEILING_TEXTURE, FLOOR_TEXTURE],
    n_repetition=5    
)
fight_scene = [fight_room] + fight_monster.objects

font = pygame.font.SysFont("arial", 32)

def get_text_button(text, key: int,  f: Callable, pos:tuple, color1: tuple = (255, 255, 255), color2: tuple = (255, 0, 0)):
    return buttons.KeyButton(
        key,
        f,

        base=buttons.ButtonDescriptor(
            display=font.render(text, True, color1),
            pos=pos
        ),

        end=buttons.ButtonDescriptor(
            display=font.render(text, True, color2),
            pos=pos
        )
    )

params = {}

f = 0
@main_3D(window, camera, map, params)
def main():
    global f

    if not params["pause"]:
        pygame.mouse.set_visible(False)
        player_light = Light(camera.origine, 1.5, 10, (1, 0.5, 0))
        filtered_world = filter_cubes(camera, map, world + [player_light])
        camera.draw_world(window, filtered_world)

        for anim in frames.frame_objects:
            anim.tick(f)

        if f % 1 == 0:
            for torch in torches + [ennemy_render]: # + [sign]
                torch.tick()
            
        if ((camera.origine.x - ennemy_render.pos.x)**2 + (camera.origine.y - ennemy_render.pos.y)**2 + (camera.origine.z - ennemy_render.pos.z)**2)**0.5 <= COLLISION_RADIUS:
            params["move"] = False
            params["pause"] = True
            params["transition"] = True
            params["start_frame"] = window.copy()
            params["map"] = False
    else:
        camera.origine = Point(L, 1, L)
        player_light = Light(camera.origine, 1, 200, (1, 0.5, 0))
        ennemy_light = Light(Point(L*3, 1, L*3), 5, 200, (1, 0, 0))

        if params["transition"]:
            start = params["start_frame"]
            end = window.copy()
            camera.pitch = 0
            camera.yaw = 0.5
            camera.draw_world(end, fight_scene + [ennemy_light, player_light], max_distance=L*6)
            fire_transition(window, start, end)
            params["transition"] = False
            params["mouse_rotation"] = False
            attack_button = get_text_button("(A)ATTACK", pygame.K_a, lambda : fight_monster_entity.damage(10), (480, 480))
            
            test_button = get_text_button("(A)ITEM1", pygame.K_a, lambda : print("ITEM1"), (480, 480))
            test2_button = get_text_button("(B)ITEM2", pygame.K_b, lambda : print("ITEM2"), (480, 515))
            exit_button = get_text_button("(X)EXIT", pygame.K_x, None, (480, 550))
            buttons.deactivate([test_button, test2_button, exit_button])

            items_button = get_text_button("(Y)ITEMS", pygame.K_y, buttons.tunnel(buttons.CURRENT_BUTTONS, [test_button, test2_button], exit_button), (480, 515))

            skills_button = get_text_button("(X)SKILLS", pygame.K_x, lambda : print("SKILLS"), (480, 550))
            
            params["ennemy_health_bar"] = Rectangle(3, 10, fight_monster.pos + Point(5, 10, 0), texture=fight_monster.face.texture)
        
        params["ennemy_health_bar"].texture = get_bar(fight_monster_entity.life, fight_monster_entity.max_life, (255, 0, 0), (0, 255, 0))
        camera.draw_world(window, fight_scene + [ennemy_light, player_light, params["ennemy_health_bar"]], max_distance=L*6)

        for b in buttons.CURRENT_BUTTONS:
            b.display(window)
    f += 1

if __name__ == "__main__":
    main()