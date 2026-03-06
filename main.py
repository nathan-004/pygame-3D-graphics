import pygame

from typing import NamedTuple

class Vector(NamedTuple):
    x: float
    y: float
    z: float

class Point(NamedTuple):
    x: float
    y: float
    z: float

class Object:
    def __init__(self, vertices:list, pos: Point):
        self.vertices = vertices
        self.pos = pos

class Camera:
    def __init__(self, origine:Point, direction: Vector, size:tuple):
        self.origine = origine
        self.direction = direction
        self.size = size
        
    def draw(self, surface: pygame.Surface, object:Object):
        pass

window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3d Graphics")
done = False

while not done:
    pygame.draw.rect(window, (0, 0, 0), (0, 0, 1280, 720))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    pygame.display.update()

exit()