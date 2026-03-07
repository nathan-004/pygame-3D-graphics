import pygame
from math import atan

from typing import NamedTuple, Optional

class Vector:
    def __init__(self, x:float, y:float, z:float):
        self.x, self.y, self.z = x, y, z

    def __mul__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return (self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return (self.x * other, self.y * other, self.z * other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be mutliplied with Vector")
        
    def __add__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return (self.x + other.x, self.y + other.y, self.z + other.z)
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

class Point(NamedTuple):
    x: float
    y: float
    z: float

class Point2D(NamedTuple):
    x: float
    y: float

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

class Frustrum:
    def __init__(self, planes:list[Plan]):
        self.planes = planes

    def get_new_line(self, start_point: Point, end_point: Point) -> tuple[Point2D]:
        for plane in self.planes:
            d1, d2 = plane.distance(start_point), plane.distance(end_point)

            if d1 < 0 and d2 < 0:
                return None
            
            if d1 < 0 or d2 < 0:
                t = d1 / (d1 - d2)

                ix = start_point.x + t * (end_point.x - start_point.x)
                iy = start_point.y + t * (end_point.y - start_point.y)
                iz = start_point.z + t * (end_point.z - start_point.z)

                intersection = Point(ix, iy, iz)

                if d1 < 0:
                    start_point = intersection
                else:
                    end_point = intersection

        return start_point, end_point
    
    @staticmethod
    def from_camera(camera):
        # Calculer le centre du plan near
        center_near = Point(
            camera.origine.x + camera.direction.x * camera.d,
            camera.origine.y + camera.direction.y * camera.d,
            camera.origine.z + camera.direction.z * camera.d
        )

        # Vecteur up initial (arbitraire, souvent (0, 1, 0))
        up_vector = Vector(0, 1, 0)

        # Calculer le vecteur right
        right_vector = cross(camera.direction, up_vector)
        right_vector = normalize(right_vector)

        # Recalculer le vecteur up orthogonal à la direction et à right_vector
        up_vector = cross(right_vector, camera.direction)
        up_vector = normalize(up_vector)

        # Calculer les points pour chaque plan latéral
        half_height = camera.size[1] / 2
        half_width = camera.size[0] / 2

        # Points pour les plans latéraux
        top_point = Point(
            center_near.x,
            center_near.y + half_height,
            center_near.z
        )
        bottom_point = Point(
            center_near.x,
            center_near.y - half_height,
            center_near.z
        )
        right_point = Point(
            center_near.x + half_width,
            center_near.y,
            center_near.z
        )
        left_point = Point(
            center_near.x - half_width,
            center_near.y,
            center_near.z
        )

        # Créer les plans
        planes = []

        # Plan near
        planes.append(Plan.plane_from_point(camera.direction, center_near))

        # Plan haut
        planes.append(Plan.plane_from_point(up_vector, top_point))

        # Plan bas
        planes.append(Plan.plane_from_point(Vector(-up_vector.x, -up_vector.y, -up_vector.z), bottom_point))

        # Plan droite
        planes.append(Plan.plane_from_point(right_vector, right_point))

        # Plan gauche
        planes.append(Plan.plane_from_point(Vector(-right_vector.x, -right_vector.y, -right_vector.z), left_point))

        return Frustrum(planes)

def add(p:Point, v:Vector):
    return Point(
        p.x + v.x,
        p.y + v.y,
        p.z + v.z
    )

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
        self.d = 300

    def draw(self, surface: pygame.Surface, object:Object):
        points_2D = []
        frustrum = Frustrum.from_camera(self)

        for p in object.points:
            points_2D.append((self.point_3D_to_2D(p), p))

        for e in object.edges:
            p1, p1_original = points_2D[e[0]]
            p2, p2_original = points_2D[e[1]]
            
            points = frustrum.get_new_line(p1_original, p2_original)
            if points is None:
                continue
            p1, p2 = points
            p1_2d = self.point_3D_to_2D(p1)
            p2_2d = self.point_3D_to_2D(p2)

            pygame.draw.line(surface, "white", p1_2d, p2_2d, 2)


    def point_3D_to_2D(self, point:Point) -> Point2D:
        p_cam = Point(point.x - self.origine.x, point.y - self.origine.y, point.z - self.origine.z)
        proj = projection_perspective(p_cam, d=self.d)

        x = proj.x + self.size[0] / 2
        y = -proj.y + self.size[1] / 2

        return Point2D(x, y)

    @property
    def fov_y(self):
        return 2 * atan(self.size[1] / 2 / self.d)

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