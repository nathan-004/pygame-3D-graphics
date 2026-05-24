import pygame
import numpy as np

def lerp_color(c1, c2, t):
    return tuple(int(max(0, min(255, c1[i] - (c2[i] - c1[i])*t))) for i in range(3))

def fire_transition(
    window: pygame.Surface, start: pygame.Surface, end: pygame.Surface,
    fire_color: tuple = (255, 100, 0),
    current_pixels=None,
    fade_steps: int = 3,
    spread_chance: float = 0.5,
):
    w, h = window.get_width(), window.get_height()
    window.blit(start, (0, 0))
    pygame.display.flip()

    if current_pixels is None:
        current_pixels = [(w // 2, h // 2)]

    pixels = pygame.surfarray.pixels3d(window)
    end_pixels = pygame.surfarray.pixels3d(end)

    visited = np.zeros((w, h), dtype=np.bool_)
    fading = {} # (x,y) -> step courant
    frontier = set()

    NEIGHBORS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]

    def activate(x, y, cur_set):
        visited[x, y] = True
        fading[(x, y)] = 0
        pixels[x, y] = fire_color
        for dx, dy in NEIGHBORS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx, ny]:
                cur_set.add((nx, ny))

    for p in current_pixels:
        activate(*p, frontier)

    fire_arr = np.array(fire_color, dtype=np.float32)

    while True:
        still_frontier = set()
        for (x, y) in frontier:
            if not visited[x, y]:
                if np.random.random() < spread_chance:
                    activate(x, y, still_frontier)
                else:
                    still_frontier.add((x, y))
        frontier = still_frontier

        if fading:
            coords = np.array(list(fading.keys()), dtype=np.int32)
            steps  = np.array(list(fading.values()), dtype=np.float32)
            xs, ys = coords[:, 0], coords[:, 1]

            t = (steps / fade_steps).reshape(-1, 1)
            end_colors = end_pixels[xs, ys].astype(np.float32)

            blended = fire_arr + (end_colors - fire_arr) * t
            blended = np.clip(blended, 0, 255).astype(np.uint8)
            pixels[xs, ys] = blended

            done_mask = steps >= fade_steps
            fading = {
                (x, y): step + 1
                for (x, y), step, d in zip(fading.keys(), steps, done_mask)
                if not d
            }

        del pixels
        del end_pixels
        pygame.display.flip()
        pixels = pygame.surfarray.pixels3d(window)
        end_pixels = pygame.surfarray.pixels3d(end)

        if not frontier and not fading:
            break