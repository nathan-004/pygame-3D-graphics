import numpy as np
from numba import njit
import pygame
from math import atan

from src.constants import L
from src.render.utils import *

@njit(fastmath = True)
def draw_triangle_numba(
    pixels,
    tex_pixels,
    zbuffer,
    width,
    height,
    x1, y1, z1, u1, v1t,
    x2, y2, z2, u2, v2t,
    x3, y3, z3, u3, v3t,
    N, camera_position,
    lights: list[tuple]
):
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

    dw1_dx = (y2 - y3) * inv_denom
    dw1_dy = (x3 - x2) * inv_denom

    dw2_dx = (y3 - y1) * inv_denom
    dw2_dy = (x1 - x3) * inv_denom

    w1_row = ((y2 - y3)*(xmin - x3) + (x3 - x2)*(ymin - y3)) * inv_denom
    w2_row = ((y3 - y1)*(xmin - x3) + (x1 - x3)*(ymin - y3)) * inv_denom

    for y in range(ymin, ymax, N):

        w1 = w1_row
        w2 = w2_row
        w3 = 1.0 - w1 - w2

        for x in range(xmin, xmax, N):

            if w1 >= 0 and w2 >= 0 and w3 >= 0:

                uz = w1*(u1/z1) + w2*(u2/z2) + w3*(u3/z3)
                vz = w1*(v1t/z1) + w2*(v2t/z2) + w3*(v3t/z3)
                iz = w1*(1.0/z1) + w2*(1.0/z2) + w3*(1.0/z3)

                z = 1.0 / iz

                if z < zbuffer[y, x]:

                    u = uz / iz
                    v = vz / iz

                    tx = int(u * (tex_w - 1))
                    ty = int((1.0 - v) * (tex_h - 1))

                    if tx < 0:
                        tx = 0
                    elif tx >= tex_w:
                        tx = tex_w - 1

                    if ty < 0:
                        ty = 0
                    elif ty >= tex_h:
                        ty = tex_h - 1

                    color = tex_pixels[tx, ty]

                    r = 0
                    g = 0
                    b = 0

                    px = (x / width) * 2 - 1
                    py = 1 - (y / height) * 2

                    xw = px * z + camera_position[0]
                    yw = py * z + camera_position[1]
                    zw = z + camera_position[2]

                    for light in lights:
                        lx, ly, lz = light[0]
                        dx = lx - xw
                        dy = ly - yw
                        dz = lz - zw

                        radius = light[3]

                        dist2 = dx*dx + dy*dy + dz*dz
                        if dist2 < radius * radius:
                            intensity = (1 / (1 + 0.5 * dist2)) * light[1]
                            
                            r += color[0] * intensity * light[2][0]
                            g += color[1] * intensity * light[2][1]
                            b += color[2] * intensity * light[2][2]

                    color = (r, g, b)

                    for yy in range(y, min(y+N, height)):
                        for xx in range(x, min(x+N, width)):
                            zbuffer[yy, xx] = z
                            pixels[xx, yy] = color

            w1 += dw1_dx * N
            w2 += dw2_dx * N
            w3 = 1.0 - w1 - w2

        w1_row += dw1_dy * N
        w2_row += dw2_dy * N

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
        self.N_MIN = 1
        self.N_MAX = 3
        self.target_pixel = 3000
        
        self.textures = {}

        self.zbuffer = None

        self.lights = []

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
        self.zbuffer = np.full((surface.get_height(), surface.get_width()), L * 3, dtype=np.float32)

        self.lights = [obj for obj in objects if isinstance(obj, Light)]
        objects = [obj for obj in objects if not isinstance(obj, Light)]

        camera_plane = Plan.plane_from_point(self.direction, self.origine)
        objects = sorted(objects, key= lambda x: camera_plane.distance(x.pos), reverse=False)

        for obj in objects:
            self.draw(surface, obj)

    def draw(self, surface: pygame.Surface, object:Object):
        NEAR = 0.5
        
        #self.draw_edges(surface, object, NEAR)
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
        if object.fill_color is None and object.texture is None:
            return
        
        pixels = pygame.surfarray.pixels3d(surface)
        for idx, points in enumerate(object.faces):
            if type(object.texture) is list:
                if object.texture[idx] is None:
                    continue
                
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
                        self.draw_triangle(pixels, self.get_current_texture(object.texture, idx), surface.get_size(), *projected)
                    else:
                        pygame.gfxdraw.filled_polygon(surface, projected, object.fill_color)
        del pixels
        if object.texture:
            for key in list(self.textures.keys()):
                del self.textures[key]

    def draw_triangle(self, pixels: pygame.surfarray.pixels3d, tex_pixels: pygame.surfarray.pixels3d, surface_size: tuple, v1: Point, v2: Point, v3: Point):
        width, height = surface_size

        x1, y1, z1, u1, v1t = v1
        x2, y2, z2, u2, v2t = v2
        x3, y3, z3, u3, v3t = v3

        area = abs(
            x1*(y2 - y3) +
            x2*(y3 - y1) +
            x3*(y1 - y2)
        ) / 2

        lights = [((light.pos.x, light.pos.y, light.pos.z), light.intensity, light.color, light.radius) for light in self.lights]

        N = min(max(int((area / self.target_pixel)**0.5), self.N_MIN), self.N_MAX)

        draw_triangle_numba(
            pixels,
            tex_pixels,
            self.zbuffer,
            width,
            height,
            x1, y1, z1, u1, v1t,
            x2, y2, z2, u2, v2t,
            x3, y3, z3, u3, v3t,
            N, (self.origine.x, self.origine.y, self.origine.z),
            lights
        )
    
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
    
    def get_current_texture(self, texture, idx):
        if type(texture) is list:
            texture = texture[idx]
        if texture in self.textures:
            return self.textures[texture]
        
        self.textures[texture] = pygame.surfarray.pixels3d(texture)
        return self.textures[texture]

    @property
    def fov_y(self):
        return 2 * atan(self.size[1] / 2 / self.d)