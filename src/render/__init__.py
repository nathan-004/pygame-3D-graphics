from math import floor
import pygame

from src.constants import L
from src.render.utils import *
from src.render.camera import Camera

from map import Map

def cross_walls(map: Map, start: Point, end: Point) -> bool:
    start_x = int(floor(start.x / L))
    start_z = int(floor(start.z / L))

    end_x = int(floor(end.x / L))
    end_z = int(floor(end.z / L))

    if start_x == end_x and start_z == end_z:
        return False

    cell = map.map[start_z][start_x]

    dx = end_x - start_x
    dz = end_z - start_z

    if dx == 1:
        return cell.walls["right"]
    if dx == -1:
        return cell.walls["left"]

    if dz == 1:
        return cell.walls["bottom"]
    if dz == -1:
        return cell.walls["top"]

    if dx != 0 and dz != 0:
        return (
            cross_walls(map, start, Point(end.x, start.y, start.z)) or
            cross_walls(map, Point(start.x, start.y, end.z), end)
        )

    return False

def is_blocked(map, x0, z0, x1, z1):
    dx = x1 - x0
    dz = z1 - z0

    steps = floor(max(abs(dx), abs(dz)))
    if steps == 0:
        return False

    prev_x, prev_z = x0, z0

    for i in range(1, steps + 1):
        x = x0 + dx * i // steps
        z = z0 + dz * i // steps

        if (x, z) != (prev_x, prev_z):
            dx_step = x - prev_x
            dz_step = z - prev_z

            prev_cell = map.map[floor(prev_z)][floor(prev_x)]
            curr_cell = map.map[floor(z)][floor(x)]

            blocked = False
            
            if dx_step > 0 and dz_step > 0:  # bas-droit
                route1_blocked = prev_cell.walls["right"] or curr_cell.walls["top"]
                route2_blocked = prev_cell.walls["bottom"] or curr_cell.walls["left"]
                blocked = route1_blocked and route2_blocked
            elif dx_step > 0 and dz_step < 0:  # haut-droit
                route1_blocked = prev_cell.walls["right"] or curr_cell.walls["bottom"]
                route2_blocked = prev_cell.walls["top"] or curr_cell.walls["left"]
                blocked = route1_blocked and route2_blocked
            elif dx_step < 0 and dz_step > 0:  # bas-gauche
                route1_blocked = prev_cell.walls["left"] or curr_cell.walls["top"]
                route2_blocked = prev_cell.walls["bottom"] or curr_cell.walls["right"]
                blocked = route1_blocked and route2_blocked
            elif dx_step < 0 and dz_step < 0:  # haut-gauche
                route1_blocked = prev_cell.walls["left"] or curr_cell.walls["bottom"]
                route2_blocked = prev_cell.walls["top"] or curr_cell.walls["right"]
                blocked = route1_blocked and route2_blocked
        
            elif dx_step > 0:  # droit
                blocked = prev_cell.walls["right"] or curr_cell.walls["left"]
            elif dx_step < 0:  # gauche
                blocked = prev_cell.walls["left"] or curr_cell.walls["right"]
            elif dz_step > 0:  # bas
                blocked = prev_cell.walls["bottom"] or curr_cell.walls["top"]
            elif dz_step < 0:  # haut
                blocked = prev_cell.walls["top"] or curr_cell.walls["bottom"]
            
            if blocked:
                return True

        prev_x, prev_z = x, z

    return False

def filter_cubes(camera: Camera, map: Map, objects: list[Object]) -> list:
    new_objects = []
    blocked = {}

    cur_x = floor(camera.origine.x / L)
    cur_z = floor(camera.origine.z / L)

    for obj in objects:
        if isinstance(obj, Light):
            new_objects.append(obj)
        map_x = floor(obj.pos.x / L)
        map_z = floor(obj.pos.z / L)

        dx = map_x - cur_x
        dz = map_z - cur_z

        dist = (dx*dx + dz*dz)**0.5
        if dist == 0:
            new_objects.append(obj)
            continue
        
        if dist >= L * 5:
            continue

        dir_x = round(dx / dist, 2)
        dir_z = round(dz / dist, 2)
        direction = (dir_x, dir_z)

        if direction in blocked:
            if dist > blocked[direction]:
                continue

        if is_blocked(map, cur_x, cur_z, map_x, map_z):
            blocked[direction] = dist
            continue

        new_objects.append(obj)

    return new_objects

def main_3D(window: pygame.Surface, camera: Camera, map: Map):
    def main_3D(func):
        def wrapper():
            # Initialisation
            map_surface = pygame.Surface((300, 300))
            pygame.mouse.set_visible(False)
            pygame.font.init()

            clock = pygame.time.Clock()
            font = pygame.font.Font(None, 24)

            speed_move = 3
            done = False
            debug = True
            collision = True

            f = 0

            # Main loop
            while not done:
                f += 1
                fps = clock.get_fps()
                pygame.draw.rect(window, (0, 0, 0), (0, 0, window.get_width(), window.get_height()))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            debug = not debug
                        if event.key == pygame.K_ESCAPE:
                            done = True
                        if event.key == pygame.K_c:
                            collision = not collision

                keys = pygame.key.get_pressed()
                
                right = cross(camera.direction,Vector(0,1,0))
                forward = normalize(cross(right, Vector(1,1,0)))

                move = Vector(0,0,0)

                cur_speed_move = speed_move

                if keys[pygame.K_UP] or keys[pygame.K_z]:
                    move = move - forward

                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    move = move + forward

                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    move = move - right

                if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                    move = move + right

                if keys[pygame.K_LSHIFT]:
                    cur_speed_move += 2

                if dot(move, move) != 0:
                    move = normalize(move)

                func()

                if debug:
                    origine_text = f"Origine: ({camera.origine.x:.2f}, {camera.origine.y:.2f}, {camera.origine.z:.2f})"
                    direction_text = f"Direction: ({camera.direction.x:.2f}, {camera.direction.y:.2f}, {camera.direction.z:.2f})"
                    
                    fps_surface = font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
                    origine_surface = font.render(origine_text, True, (0, 255, 0))
                    direction_surface = font.render(direction_text, True, (0, 255, 0))
                    
                    window.blit(fps_surface, (10, 10))
                    window.blit(origine_surface, (10, 35))
                    window.blit(direction_surface, (10, 60))
                    
                    highlited = [(floor(obj.pos.x / L), floor(obj.pos.z / L)) for obj in camera.latest_draw]
                    
                    map.draw(map_surface, (floor(camera.origine.x / L), floor(camera.origine.z / L)), (camera.direction.x, camera.direction.z), highlited = highlited)
                    window.blit(map_surface, (10, 80))

                mov = pygame.mouse.get_rel()
                sens = 0.1
                dt = clock.tick(60) / 1000

                camera.yaw   += mov[0] * sens * dt
                camera.pitch -= mov[1] * sens * dt
                MAX_PITCH = 1.55
                camera.pitch = max(-MAX_PITCH, min(MAX_PITCH, camera.pitch))

                if f % 2 == 0:
                    pygame.mouse.set_pos((window.get_width() / 2, window.get_height() / 2))
                pygame.display.update()
                
                start = camera.origine
                end = move * dt * cur_speed_move * Vector(1, 0, 1) + camera.origine
                
                if collision:
                    if cross_walls(map, start, end):
                        continue
                camera.origine = end

            exit()
        return wrapper
    return main_3D
