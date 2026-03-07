import pygame
from math import atan, cos, sin, pi

from typing import NamedTuple

class Vector:
    def __init__(self, x:float, y:float, z:float):
        self.x, self.y, self.z = x, y, z

    def __mul__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return type(other)(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be mutliplied with Vector")
        
    def __add__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return type(other)(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return (self.x + other, self.y + other, self.z + other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Vector")
    
    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return (self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return (self.x - other, self.y - other, self.z - other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Vector")
    
    def __str__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

class Point(NamedTuple):
    x: float
    y: float
    z: float

    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return (self.x - other, self.y - other, self.z - other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Point")

class Point2D(NamedTuple):
    x:float
    y:float

class Plan:
    def __init__(self, normal:Vector, d:float):
        self.normal = normal
        self.d = d

    def distance(self, point:Point) -> float:
        return dot(self.normal, point) + self.d
    
    @staticmethod
    def plane_from_point(normal, point):
        distance = -dot(normal, point)
        return Plan(normal, distance)

def dot(v1:Vector, v2:Vector) -> float:
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

def cross(v1:Vector, v2:Vector) -> Vector:
    return Vector(
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )

def normalize(v:Vector) -> Vector:
    l = dot(v, v) ** 0.5
    return Vector(v.x/l, v.y/l, v.z/l)

def projection_perspective(p:Point, d:float) -> Point2D:
    return Point2D(p.x * (d / p.z), p.y * (d / p.z))

def intersect_near(p1: Point, p2: Point, near:float):
    t = (near - p1.z) / (p2.z - p1.z)

    x = p1.x + t * (p2.x - p1.x)
    y = p1.y + t * (p2.y - p1.y)
    z = near

    return Point(x, y, z)

class Object:
    def __init__(self, vertices:list, edges:list, pos: Point):
        self._vertices = vertices
        self.edges = edges
        self.pos = pos

    @property
    def points(self):
        return [Point(point.x + self.pos.x, point.y + self.pos.y, point.z + self.pos.z) for point in self._vertices]
    
class Cube(Object):
    def __init__(self, l, pos):
        vertices = [
            Point(0, 0, 0),
            Point(0, l, 0),
            Point(l, l, 0),
            Point(l, 0, 0),

            Point(0, 0, l),
            Point(0, l, l),
            Point(l, l, l),
            Point(l, 0, l)
        ]

        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]

        super().__init__(vertices, edges, pos)

class Camera:
    def __init__(self, origine:Point, size:tuple, yaw:float = 0, pitch:float = 0):
        self.origine = origine

        self.yaw = yaw # Rotation gauche/droite
        self.pitch = pitch # Rotation haut/bas

        self.size = size
        self.d = 300

    @property
    def direction(self):
        return normalize(Vector(
            cos(self.pitch) * sin(self.yaw),
            sin(self.pitch),
            cos(self.pitch) * cos(self.yaw)
        ))

    def draw(self, surface: pygame.Surface, object:Object):
        NEAR = 0.01

        for e in object.edges:
            p1 = self.world_to_camera(object.points[e[0]]) - self.origine
            p2 = self.world_to_camera(object.points[e[1]]) - self.origine

            if p1.z < NEAR and p2.z < NEAR:
                continue

            if p1.z < NEAR:
                p1 = intersect_near(p1, p2, NEAR)

            if p2.z < NEAR:
                p2 = intersect_near(p2, p1, NEAR)

            p1_2d = projection_perspective(p1, self.d)
            p2_2d = projection_perspective(p2, self.d)

            x1 = p1_2d.x + self.size[0] / 2
            y1 = -p1_2d.y + self.size[1] / 2

            x2 = p2_2d.x + self.size[0] / 2
            y2 = -p2_2d.y + self.size[1] / 2

            pygame.draw.line(surface, "white", (x1,y1), (x2,y2), 2)

    def point_3D_to_2D(self, point:Point) -> Point2D:
        p_cam = Point(point.x - self.origine.x, point.y - self.origine.y, point.z - self.origine.z)
        proj = projection_perspective(p_cam, d=self.d)

        x = proj.x + self.size[0] / 2
        y = -proj.y + self.size[1] / 2

        return Point2D(x, y)
    
    def world_to_camera(self, point):
        forward = normalize(self.direction)
        world_up = Vector(0,1,0)

        right = normalize(cross(forward, world_up))
        up = cross(right, forward)

        rel = Vector(
            point.x - self.origine.x,
            point.y - self.origine.y,
            point.z - self.origine.z
        )

        x = dot(rel, right)
        y = dot(rel, up)
        z = dot(rel, forward)

        return Point(x, y, z)

    @property
    def fov_y(self):
        return 2 * atan(self.size[1] / 2 / self.d)

window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3d Graphics")
pygame.mouse.set_visible(False)

camera = Camera(Point(0,0,0), (1280,720))

c1 = Cube(5, Point(1, 0, 6))
c2 = Cube(10, Point(1, 0, 11))

speed_move = 0.007
done = False

f = 0

while not done:
    f += 1
    pygame.draw.rect(window, (0, 0, 0), (0, 0, 1280, 720))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()

    cur_a = 0
    if keys[pygame.K_LEFT]: cur_a -= pi / 2
    if keys[pygame.K_RIGHT]: cur_a += pi / 2
    if keys[pygame.K_UP]: cur_a += 0.000001
    if keys[pygame.K_DOWN]:cur_a -= pi

    rotated = Vector(
        cos(cur_a) * camera.direction.x + sin(cur_a) * camera.direction.z,
        0,
        sin(cur_a) * -camera.direction.x + cos(cur_a) * camera.direction.z
    )

    if cur_a != 0:
        print(camera.origine)
        camera.origine = rotated * speed_move + camera.origine
 
    camera.draw(window, c1)
    camera.draw(window, c2)
    
    mov = pygame.mouse.get_rel()
    sens = 0.003

    camera.yaw   -= mov[0] * sens
    camera.pitch -= mov[1] * sens
    MAX_PITCH = 1.55
    camera.pitch = max(-MAX_PITCH, min(MAX_PITCH, camera.pitch))

    if f % 50 == 0:
        pygame.mouse.set_pos((window.get_width() / 2, window.get_height() / 2))
    pygame.display.update()

exit()