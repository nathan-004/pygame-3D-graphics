from math import cos, sin, floor
import random
import pygame

from typing import NamedTuple, Callable
from copy import deepcopy

from src.render.text import correct_text_placement
from src.constants import L, TORCH_TEXTURE, DISPLAY_SIGN

def get_x_rotation_matrix(theta) -> list:
    return [
        [1, 0, 0],
        [0, cos(theta), -sin(theta)],
        [0, sin(theta), cos(theta)]
    ]

def get_y_rotation_matrix(theta) -> list:
    return [
        [cos(theta), 0, sin(theta)],
        [0, 1, 0],
        [-sin(theta), 0, cos(theta)]
    ]

def get_z_rotation_matrix(theta) -> list:
    return [
        [cos(theta), -sin(theta), 0],
        [sin(theta), cos(theta), 0],
        [0, 0, 1]
    ]

class Vector:
    def __init__(self, x:float, y:float, z:float):
        self.x, self.y, self.z = x, y, z

    def __mul__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            if isinstance(other, Point):
                return Point(self.x * other.x, self.y * other.y, self.z * other.z, other.u, other.v)
            return type(other)(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be mutliplied with Vector")
        
    def __add__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            if isinstance(other, Point):
                return Point(self.x + other.x, self.y + other.y, self.z + other.z, other.u, other.v)
            return type(other)(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x + other, self.y + other, self.z + other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Vector")
    
    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            if isinstance(other, Point):
                return Point(self.x - other.x, self.y - other.y, self.z - other.z, other.u, other.v)
            return type(other)(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x - other, self.y - other, self.z - other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Vector")
    
    def __str__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

class Point(NamedTuple):
    x: float
    y: float
    z: float
    u: float = 0
    v: float = 0

    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y, self.z - other.z, self.u, self.v)
        elif isinstance(other, float) or isinstance(other, int):
            return Point(self.x - other, self.y - other, self.z - other, self.u, self.v)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Point")
        
    def __add__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z, self.u, self.v)
        elif isinstance(other, float) or isinstance(other, int):
            return Point(self.x + other, self.y + other, self.z + other, self.u, self.v)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Point")
        
    def __mul__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            if isinstance(other, Point):
                return Point(self.x * other.x, self.y * other.y, self.z * other.z, other.u, other.v)
            return type(other)(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be mutliplied with Vector")

class Point2D(NamedTuple):
    x:float
    y:float
    x_original:float = 0.0
    y_original:float = 0.0

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

def signed_triangle_area(p1: Point, p2: Point, p3:Point):
    return abs(dot((p2 - p1) * Vector(1, 1, 0), (p3 - p2) * Vector(1, 1, 0)))

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
    u = p1.u + t * (p2.u - p1.u)
    v = p1.v + t * (p2.v - p1.v)

    return Point(x, y, z, u, v)

def rotate_point(p: Point, rotation_matrix: list) -> Point:
    return Point(
        p.x * rotation_matrix[0][0] + p.y * rotation_matrix[0][1] + p.z * rotation_matrix[0][2],
        p.x * rotation_matrix[1][0] + p.y * rotation_matrix[1][1] + p.z * rotation_matrix[1][2],
        p.x * rotation_matrix[2][0] + p.y * rotation_matrix[2][1] + p.z * rotation_matrix[2][2],
        p.u, p.v
    )

class Object:
    def __init__(self, vertices:list, edges:list, faces:list, pos: Point, fill_color: pygame.Color = None, texture: pygame.Surface = None):
        if type(fill_color) is list:
            assert len(fill_color) == len(faces), "Nombre de couleurs différent du nombre de faces"
        elif type(texture) is list:
            assert len(texture) == len(faces), "Nombre de textures spécifiés différents du nombre de faces"
        
        self._vertices = vertices
        self.edges = edges
        self.pos = pos
        self.faces = faces
        self.fill_color = fill_color
        self.texture = texture

    @property
    def points(self):
        return [Point(point.x + self.pos.x, point.y + self.pos.y, point.z + self.pos.z, point.u, point.v) for point in self._vertices]
    
    def transformation(self, f: Callable):
        for idx, p in enumerate(self._vertices):
            self._vertices[idx] = f(p)

class Light:
    def __init__(self, pos:Point, intensity:float = 0.5, radius:float = 7, color:tuple = (1,1,1)):
        self.pos = pos
        self.intensity = intensity
        self.color = color
        self.radius = radius

class Cuboid(Object):
    def __init__(self, l, L, h, pos, color:pygame.Color = None, texture: pygame.Surface = None):
        vertices = [
            # Front
            Point(0, 0, 0, 0, 0),
            Point(0, h, 0, 0, 1),
            Point(L, h, 0, 1, 1),
            Point(L, 0, 0, 1, 0),

            # Back
            Point(0, 0, l, 0, 0),
            Point(0, h, l, 0, 1),
            Point(L, h, l, 1, 1),
            Point(L, 0, l, 1, 0),

            # Left
            Point(0, h, l, 1, 1),
            Point(0, 0, l, 1, 0),

            # Right
            Point(L, 0, 0, 0, 0),
            Point(L, h, 0, 0, 1),

            # Top
            Point(0, h, 0, 0, 0),
            Point(L, h, 0, 1, 0),

            # Bottom
            Point(0, 0, l, 0, 1),
            Point(L, 0, l, 1, 1),
        ]


        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        
        faces = [
            (0, 1, 2, 3), # Front
            (4, 5, 6, 7), # Back
            
            (0, 1, 8, 9), # Left
            (11, 10, 7, 6), # Right
            
            (12, 5, 6, 13), # Top
            (0, 14, 15, 3)
        ]

        super().__init__(vertices, edges, faces, pos, color, texture)

class Cube(Object):
    def __init__(self, l, pos, color:pygame.Color = None, texture: pygame.Surface = None):
        vertices = [
            # Front
            Point(0, 0, 0, 0, 0),
            Point(0, l, 0, 0, 1),
            Point(l, l, 0, 1, 1),
            Point(l, 0, 0, 1, 0),

            # Back
            Point(0, 0, l, 0, 0),
            Point(0, l, l, 0, 1),
            Point(l, l, l, 1, 1),
            Point(l, 0, l, 1, 0),

            # Left
            Point(0, l, l, 1, 1),
            Point(0, 0, l, 1, 0),

            # Right
            Point(l, 0, 0, 0, 0),
            Point(l, l, 0, 0, 1),

            # Top
            Point(0, l, 0, 0, 0),
            Point(l, l, 0, 1, 0),

            # Bottom
            Point(0, 0, l, 0, 1),
            Point(l, 0, l, 1, 1),
        ]


        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        
        faces = [
            (0, 1, 2, 3), # Front
            (4, 5, 6, 7), # Back
            
            (0, 1, 8, 9), # Left
            (11, 10, 7, 6), # Right
            
            (12, 5, 6, 13), # Top
            (0, 14, 15, 3)
        ]

        super().__init__(vertices, edges, faces, pos, color, texture)
        
class Square(Object):
    def __init__(self, l, pos, color:pygame.Color = None, texture: pygame.Surface = None, rotation_x:float = 0, rotation_y:float = 0, rotation_z:float = 0):
        vertices = [
            Point(0, 0, 0, 0, 0),
            Point(0, l, 0, 0, 1),
            Point(l, l, 0, 1, 1),
            Point(l, 0, 0, 1, 0),
        ]

        # Appliquer les rotations
        vertices = self._rotate_vertices(vertices, rotation_x, rotation_y, rotation_z)

        edges = [
            (0,1),(1,2),(2,3),(3,0),
        ]
        
        faces = [
            (0, 1, 2, 3),
        ]

        super().__init__(vertices, edges, faces, pos, color, texture)

    @staticmethod
    def _rotate_vertices(vertices, rot_x, rot_y, rot_z):
        """Applique les rotations (en radians) aux vertices"""
        rotated = []
        
        for v in vertices:
            # Rotation autour de X
            y = v.y * cos(rot_x) - v.z * sin(rot_x)
            z = v.y * sin(rot_x) + v.z * cos(rot_x)
            
            # Rotation autour de Y
            x = v.x * cos(rot_y) + z * sin(rot_y)
            z = -v.x * sin(rot_y) + z * cos(rot_y)
            
            # Rotation autour de Z
            x_new = x * cos(rot_z) - y * sin(rot_z)
            y = x * sin(rot_z) + y * cos(rot_z)
            
            rotated.append(Point(x_new, y, z, v.u, v.v))
        
        return rotated
    
class Element:
    """Ensemble d'objets avec possibilité d'appeler une fonction à chaque frame"""
    def __init__(self, objects: list):
        self.objects = objects
    
    def tick(self):
        pass

class Torch(Element):
    """Objet torche contenant le support + lumière"""

    def __init__(self, position: Point, color:tuple = (1, 0, 0)):
        self.color = color
        self.support = Cuboid(0.15, 0.15, 1, position, texture=TORCH_TEXTURE)
        self.light = Light(position + Point(0, 1, 0), intensity=1, color=color)
        
        self.variation = 0
        self.max_variation, self.min_variation = 0.5, 0
        self.middle_variation = (self.max_variation + self.min_variation) / 2

        super().__init__([self.support, self.light])

    def tick(self):
        self.light.color = (self.color[0], self.color[1] + self.variation, self.color[2])
        
        negatives = [-random.random()*0.01] * int(abs(self.variation - self.min_variation)*10)
        positives = [random.random()*0.01] * int(abs(self.variation - self.max_variation)*10)
        self.variation += random.choice(negatives + positives)
        self.variation = min(self.max_variation, max(self.min_variation, self.variation))

class Sign(Element):
    """Objet Panneau contenant le support + le panneau en lui-même"""

    def __init__(self, display: pygame.Surface, pos: Point, support: bool = False):
        self.display = Cuboid(0.01, 0.5, 1, pos, texture=[display, DISPLAY_SIGN, DISPLAY_SIGN, DISPLAY_SIGN, DISPLAY_SIGN, DISPLAY_SIGN])

        super().__init__([self.display])

    @staticmethod
    def from_text(text: str, pos: Point, support: bool = False):
        display = DISPLAY_SIGN.copy()
        
        correct_text_placement(text, display)

        return Sign(display, pos, support)