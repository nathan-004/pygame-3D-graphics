import pygame
import pygame.gfxdraw
from math import atan, cos, sin, radians

from typing import NamedTuple

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

class Object:
    def __init__(self, vertices:list, edges:list, faces:list, pos: Point, fill_color: pygame.Color = None, texture: pygame.Surface = None):
        if fill_color is None and texture is None:
            fill_color = (0, 255, 255)
        assert fill_color is not None or texture is not None, "Une couleur ou une texture doit être spécifié"

        self._vertices = vertices
        self.edges = edges
        self.pos = pos
        self.faces = faces
        self.fill_color = fill_color
        self.texture = texture

    @property
    def points(self):
        return [Point(point.x + self.pos.x, point.y + self.pos.y, point.z + self.pos.z, point.u, point.v) for point in self._vertices]
    
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

def face_to_triangles(points:list) -> list:
    triangles = []
    for i in range(1, len(points)-1):
        triangles.append((points[0], points[i], points[i+1]))
    return triangles

class Camera:
    def __init__(self, origine:Point, size:tuple, yaw:float = 0, pitch:float = 0):
        self.origine = origine

        self.yaw = yaw # Rotation gauche/droite
        self.pitch = pitch # Rotation haut/bas

        self.size = size
        self.d = 1
        self.N = 4

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

    def draw_world(self, surface:pygame.Surface, objects: list[Object]):
        camera_plane = Plan.plane_from_point(self.direction, self.origine)
        objects = sorted(objects, key= lambda x: camera_plane.distance(x.pos), reverse=True)

        for obj in objects:
            self.draw(surface, obj)

    def draw(self, surface: pygame.Surface, object:Object):
        NEAR = 0.5
        
        self.draw_edges(surface, object, NEAR)
        self.draw_faces(surface, object, NEAR)

    def draw_edges(self, surface: pygame.Surface, object: Object, near:float):
        for e in object.edges:
            p1 = self.world_to_camera(object.points[e[0]])
            p2 = self.world_to_camera(object.points[e[1]])

            if p1.z < near and p2.z < near:
                continue

            if p1.z < near:
                p1 = intersect_near(p1, p2, near)

            if p2.z < near:
                p2 = intersect_near(p2, p1, near)

            p1_2d = projection_perspective(p1, self.d)
            p2_2d = projection_perspective(p2, self.d)

            pygame.draw.line(surface, "white", self.screen(p1_2d, surface), self.screen(p2_2d, surface), 2)

    def draw_faces(self, surface: pygame.Surface, object:Object, near: float):
        pixels = pygame.surfarray.pixels3d(surface)
        if object.texture:
            texture_pixels = pygame.surfarray.pixels3d(object.texture)
        for points in object.faces:
            cam_points = [self.world_to_camera(object.points[i]) for i in points]

            if all(p.z < near for p in cam_points):
                continue

            clipped = []

            for p1, p2 in zip(cam_points, cam_points[1:] + cam_points[:1]):
                if p1.z >= near and p2.z >= near:
                    clipped.append(p2)

                elif p1.z >= near and p2.z < near:
                    clipped.append(intersect_near(p1, p2, near))

                elif p1.z < near and p2.z >= near:
                    clipped.append(intersect_near(p1, p2, near))
                    clipped.append(p2)

            if len(clipped) >= 3:
                triangles = face_to_triangles(clipped)
                for triangle in triangles:
                    projected = []
                    for v in triangle:
                        p2d = projection_perspective(v, self.d)
                        screen_p = self.screen(p2d, surface)
                        projected.append(Point(screen_p.x, screen_p.y, v.z, v.u, v.v))
                    if object.texture:
                        self.draw_triangle(pixels, texture_pixels, surface.get_size(), *projected)
                    else:
                        pygame.gfxdraw.filled_polygon(surface, projected, object.fill_color)
        del pixels
        if object.texture:
            del texture_pixels

    def draw_triangle(self, pixels: pygame.surfarray.pixels3d, tex_pixels: pygame.surfarray.pixels3d, surface_size: tuple, v1: Point, v2: Point, v3: Point):
        N = self.N

        width, height = surface_size
        x1, y1, z1, u1, v1t = v1
        x2, y2, z2, u2, v2t = v2
        x3, y3, z3, u3, v3t = v3

        xmin = max(0, int(min(x1, x2, x3)))
        xmax = min(width - 1, int(max(x1, x2, x3)))

        ymin = max(0, int(min(y1, y2, y3)))
        ymax = min(height - 1, int(max(y1, y2, y3)))

        denom = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)
        if denom == 0:
            return

        inv_denom = 1.0 / denom

        tex_w = tex_pixels.shape[0]
        tex_h = tex_pixels.shape[1]

        # dérivées barycentriques
        dw1_dx = (y2 - y3) * inv_denom
        dw1_dy = (x3 - x2) * inv_denom

        dw2_dx = (y3 - y1) * inv_denom
        dw2_dy = (x1 - x3) * inv_denom

        # point de départ
        w1_row = ((y2 - y3)*(xmin - x3) + (x3 - x2)*(ymin - y3)) * inv_denom
        w2_row = ((y3 - y1)*(xmin - x3) + (x1 - x3)*(ymin - y3)) * inv_denom

        for y in range(ymin, ymax, N):
            w1 = w1_row
            w2 = w2_row
            w3 = 1 - w1 - w2

            for x in range(xmin, xmax, N):
                if w1 >= 0 and w2 >= 0 and w3 >= 0:
                    uz = w1*(u1/z1) + w2*(u2 / z2) + w3*(u3 / z3)
                    vz = w1*(v1t/z1) + w2*(v2t/z2) + w3*(v3t/z3)
                    iz = w1*(1/z1) + w2*(1/z2) + w3*(1/z3)

                    u = uz / iz
                    v = vz / iz

                    tx = int(u * (tex_w-1))
                    ty = int((1.0 - v) * (tex_h-1))

                    color = tex_pixels[tx, ty]

                    pixels[x:x+N, y:y+N] = color

                # incrément horizontal
                w1 += dw1_dx * N
                w2 += dw2_dx * N
                w3 = 1 - w1 - w2

            # incrément vertical
            w1_row += dw1_dy * N
            w2_row += dw2_dy * N
    
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

        return Point(x, y, z, point.u, point.v)

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
TEXTURE = pygame.image.load("assets/texture_test.jpg")

c1 = Cube(5, Point(0, 0, 6))
c2 = Cube(10, Point(0, 0, 11), texture=TEXTURE)
s1 = Square(10, Point(-5, 0, 15), texture=TEXTURE, rotation_y=radians(90))
s2 = Square(10, Point(-5.0001, 0.0001, 15.001), texture=TEXTURE)
s3 = Square(10, Point(5, 0, 15), texture=TEXTURE, rotation_y=radians(90))

world = [c2]

speed_move = 3
done = False
debug = True

f = 0

while not done:
    f += 1
    fps = clock.get_fps()
    pygame.draw.rect(window, (0, 100, 255), (0, 0, 1280, 720))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                debug = not debug
            if event.key == pygame.K_ESCAPE:
                done = True

    keys = pygame.key.get_pressed()
    
    forward = normalize(camera.direction)
    right = normalize(cross(forward, Vector(0,1,0)))
    top = Vector(0, 1, 0)

    move = Vector(0,0,0)

    if keys[pygame.K_UP] or keys[pygame.K_z]:
        move = move + forward

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move = move - forward

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move = move - right

    if keys[pygame.K_LEFT] or keys[pygame.K_q]:
        move = move + right

    if keys[pygame.K_LSHIFT]:
        move = move + top

    if keys[pygame.K_LCTRL]:
        move = move - top

    if dot(move, move) != 0:
        move = normalize(move)
 
    camera.draw_world(window, world)

    if debug:
        origine_text = f"Origine: ({camera.origine.x:.2f}, {camera.origine.y:.2f}, {camera.origine.z:.2f})"
        direction_text = f"Direction: ({camera.direction.x:.2f}, {camera.direction.y:.2f}, {camera.direction.z:.2f})"
        
        fps_surface = font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        origine_surface = font.render(origine_text, True, (0, 255, 0))
        direction_surface = font.render(direction_text, True, (0, 255, 0))
        
        window.blit(fps_surface, (10, 10))
        window.blit(origine_surface, (10, 35))
        window.blit(direction_surface, (10, 60))
    
    mov = pygame.mouse.get_rel()
    sens = 0.03
    dt = clock.tick(60) / 1000

    camera.yaw   += mov[0] * sens * dt
    camera.pitch -= mov[1] * sens * dt
    MAX_PITCH = 1.55
    camera.pitch = max(-MAX_PITCH, min(MAX_PITCH, camera.pitch))

    if f % 2 == 0:
        pygame.mouse.set_pos((window.get_width() / 2, window.get_height() / 2))
    pygame.display.update()

    camera.origine = move * dt * speed_move * Vector(1, 1, 1) + camera.origine

exit()

