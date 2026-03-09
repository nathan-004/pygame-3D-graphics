import pygame
from math import atan, cos, sin

from typing import NamedTuple
from time import perf_counter

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
            return Vector(self.x + other, self.y + other, self.z + other)
        else:
            raise NotImplementedError(f"{type(other)} cannot be additioned with Vector")
    
    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
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

    def __sub__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Point(self.x - other, self.y - other, self.z - other)
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
    def __init__(self, vertices:list, edges:list, faces:list, pos: Point):
        self._vertices = vertices
        self.edges = edges
        self.pos = pos
        self.faces = faces

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
        
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            
            (0, 1, 5, 4),
            (2, 3, 7, 6)
        ]

        super().__init__(vertices, edges, faces, pos)

class Camera:
    def __init__(self, origine:Point, size:tuple, yaw:float = 0, pitch:float = 0):
        self.origine = origine

        self.yaw = yaw # Rotation gauche/droite
        self.pitch = pitch # Rotation haut/bas

        self.size = size
        self.d = 1

    @property
    def direction(self):
        return normalize(Vector(
            cos(self.pitch) * sin(self.yaw),
            sin(self.pitch),
            cos(self.pitch) * cos(self.yaw)
        ))
    
    @property
    def view_matrix(self): 
        forward = normalize(self.direction)
        world_up = Vector(0,1,0)

        right = normalize(cross(world_up, forward))
        up = cross(forward, right)

        return [
            [right.x, right.y, right.z],
            [up.x,    up.y,    up.z],
            [forward.x, forward.y, forward.z]
        ]

    def draw(self, surface: pygame.Surface, object:Object):
        NEAR = 0.01
        
        start_edges = perf_counter()
        for e in object.edges:
            p1 = self.world_to_camera(object.points[e[0]])
            p2 = self.world_to_camera(object.points[e[1]])

            if p1.z < NEAR and p2.z < NEAR:
                continue

            if p1.z < NEAR:
                p1 = intersect_near(p1, p2, NEAR)

            if p2.z < NEAR:
                p2 = intersect_near(p2, p1, NEAR)

            p1_2d = projection_perspective(p1, self.d)
            p2_2d = projection_perspective(p2, self.d)

            pygame.draw.line(surface, "white", self.screen(p1_2d, surface), self.screen(p2_2d, surface), 2)
        end_edges = perf_counter()
        print(f"Edges drawing duration : {end_edges - start_edges}")
        
        start_face = perf_counter()
        for points in object.faces:
            start_cam = perf_counter()
            cam_points = [self.world_to_camera(object.points[point]) for point in points]
            end_cam = perf_counter() 
            #print(f"Camera conver duration : {end_cam - start_cam}")

            points_2D = []
            i = 0
            
            start_point = perf_counter()
            for p1, p2 in zip(cam_points[:-1], cam_points[1:]):
                if p1.z < NEAR and p2.z < NEAR:
                    continue
                if p1.z < NEAR:
                    p1 = intersect_near(p1, p2, NEAR)
                if p2.z < NEAR:
                    p2 = intersect_near(p2, p1, NEAR)
                
                points_2D.append(self.screen(projection_perspective(p1, self.d), surface))
                points_2D.append(self.screen(projection_perspective(p2, self.d), surface))
            end_point = perf_counter()
            #print(f"Point calculation      : {end_point - start_point}")
            
            start_polygon = perf_counter()
            if len(points_2D) > 2:
                pygame.draw.polygon(surface, "red", points_2D)
            end_polygon = perf_counter() 
            print(f"Polygon drawing        : {end_polygon - start_polygon}")
        end_face = perf_counter()
        print(f"Faces drawing duration : {end_face-start_face}")

    def screen(self, p: Point2D, surface: pygame.Surface) -> Point2D:
        w, h = surface.get_size()
        return Point2D(
            (p.x + 1) / 2 * w,
            (1 - (p.y + 1) / 2) * h
        )
    
    def world_to_camera(self, point):

        rel = Vector(
            point.x - self.origine.x,
            point.y - self.origine.y,
            point.z - self.origine.z
        )

        m = self.view_matrix

        x = rel.x*m[0][0] + rel.y*m[0][1] + rel.z*m[0][2]
        y = rel.x*m[1][0] + rel.y*m[1][1] + rel.z*m[1][2]
        z = rel.x*m[2][0] + rel.y*m[2][1] + rel.z*m[2][2]

        return Point(x,y,z)

    @property
    def fov_y(self):
        return 2 * atan(self.size[1] / 2 / self.d)

window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3d Graphics")
pygame.mouse.set_visible(False)
pygame.font.init()

camera = Camera(Point(0,1,0), (1280,720))

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

c1 = Cube(5, Point(0, 0, 6))
c2 = Cube(10, Point(0, 0, 11))

speed_move = 0.1
done = False
debug = False

f = 0

while not done:
    start_frame = perf_counter()
    f += 1
    pygame.draw.rect(window, (0, 0, 0), (0, 0, 1280, 720))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                debug = not debug

    keys = pygame.key.get_pressed()
    
    forward = normalize(camera.direction)
    right = normalize(cross(forward, Vector(0,1,0)))

    move = Vector(0,0,0)

    if keys[pygame.K_UP]:
        move = move + forward

    if keys[pygame.K_DOWN]:
        move = move - forward

    if keys[pygame.K_RIGHT]:
        move = move - right

    if keys[pygame.K_LEFT]:
        move = move + right

    if dot(move, move) != 0:
        move = normalize(move)
        
    if debug:
        fps = clock.get_fps()
        origine_text = f"Origine: ({camera.origine.x:.2f}, {camera.origine.y:.2f}, {camera.origine.z:.2f})"
        direction_text = f"Direction: ({camera.direction.x:.2f}, {camera.direction.y:.2f}, {camera.direction.z:.2f})"
        
        fps_surface = font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        origine_surface = font.render(origine_text, True, (0, 255, 0))
        direction_surface = font.render(direction_text, True, (0, 255, 0))
        
        window.blit(fps_surface, (10, 10))
        window.blit(origine_surface, (10, 35))
        window.blit(direction_surface, (10, 60))

    camera.origine = move * speed_move * Vector(1, 1, 1) + camera.origine
 
    camera.draw(window, c1)
    camera.draw(window, c2)
    
    mov = pygame.mouse.get_rel()
    sens = 0.003

    camera.yaw   += mov[0] * sens
    camera.pitch -= mov[1] * sens
    MAX_PITCH = 1.55
    camera.pitch = max(-MAX_PITCH, min(MAX_PITCH, camera.pitch))

    if f % 2 == 0:
        pygame.mouse.set_pos((window.get_width() / 2, window.get_height() / 2))
    pygame.display.update()
    end_frame = perf_counter()
    print(f"Frame duration :         {end_frame - start_frame}")
    clock.tick(60)

exit()
