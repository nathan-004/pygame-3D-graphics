import pygame
import math

from typing import NamedTuple

class Vector(NamedTuple):
    x: float
    y: float
    z: float

class Point(NamedTuple):
    x: float
    y: float
    z: float

class Point2D(NamedTuple):
    x: float
    y: float

def add(p:Point, v:Vector):
    return Point(
        p.x + v.x,
        p.y + v.y,
        p.z + v.z
    )

def projection_perspective(p:Point, d:float) -> Point2D:
    return Point2D(p.x * (d / p.z), p.y * (d / p.z))

class Object:
    def __init__(self, vertices:list, edges:list, pos: Point):
        self._vertices = vertices
        self.edges = edges
        self.pos = pos

    @property
    def points(self):
        return [Point(point.x + self.pos.x, point.y + self.pos.y, point.z + self.pos.z) for point in self._vertices]

class Camera:
    def __init__(self, origine:Point, direction: Vector, size:tuple):
        self.origine = origine
        self.direction = direction
        self.size = size

    def draw(self, surface: pygame.Surface, object:Object):
        points_2D = []

        for p in object.points:
            p_cam = Point(p.x - self.origine.x, p.y - self.origine.y, p.z - self.origine.z)
            proj = projection_perspective(p_cam, d=300)

            x = proj.x + self.size[0] / 2
            y = -proj.y + self.size[1] / 2

            points_2D.append(((x, y), p_cam.z))

        for e in object.edges:
            p1, p1z = points_2D[e[0]]
            p2, p2z = points_2D[e[1]]
            if p1z < 0 or p2z < 0:
                continue
            pygame.draw.line(surface, "white", p1, p2, 2)

window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3d Graphics")

camera = Camera(Point(0,0,0), Vector(0,0,1), (1280,720))

cube = Object(
    [
        Point(-1,-1,4),
        Point(1,-1,4),
        Point(1,1,4),
        Point(-1,1,4),

        Point(-1,-1,6),
        Point(1,-1,6),
        Point(1,1,6),
        Point(-1,1,6),
    ],
    [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ],
    Point(0,0,0)
)

speed_move = 0.01
done = False

while not done:
    pygame.draw.rect(window, (0, 0, 0), (0, 0, 1280, 720))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        camera.origine = add(camera.origine, Vector(-speed_move, 0, 0))

    if keys[pygame.K_RIGHT]:
        camera.origine = add(camera.origine, Vector(speed_move, 0, 0))

    if keys[pygame.K_UP]:
        camera.origine = add(camera.origine, Vector(0, 0, speed_move))

    if keys[pygame.K_DOWN]:
        camera.origine = add(camera.origine, Vector(0, 0, -speed_move))

    camera.draw(window, cube)

    pygame.display.update()

exit()