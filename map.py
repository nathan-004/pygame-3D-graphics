import pygame

from collections import deque
import random

class Room:
    def __init__(self):
        self.walls = {
            "left": True,
            "right": True,
            "top": True,
            "bottom": True
        }

class Map:
    def __init__(self, size: tuple, map:list = None):
        self.width, self.height = size
        
        if map is None:
            self.map = [[Room() for _ in range(self.width)] for _ in range(self.height)]
        else:
            self.map = map

    @staticmethod
    def from_map(map:list):
        return Map(
            (len(map[0]), len(map)),
            map
        )

    @staticmethod
    def random(size:tuple):
        m = Map.from_map(
            Map(size)._create_maze((0, 1))
        )
        m.create_image()
        return m
    
    def _create_maze(self, start_pos:tuple):
        """
        Créé le labyrinthe autour du chemin principale (`random_path`)

        Algorithme :
        1. Initier une Pile des cellules à observer
        2. Tant que toutes les cellules n'ont pas été visitées
        3.     Prendre la dernière cellule de la Pile ou une cellule active aléatoire
        4.     Sélectionner une direction aléatoire puis ajouter à la Pile si visitable
        """
        grid = [[Room() for _ in range(self.width)] for _ in range(self.height)]
        visited = set()
        stack = [start_pos]
        
        visited.add(start_pos)

        while len(stack) > 0:
            x, y = stack[-1]
            
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)
            
            found_unvisited = False

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    found_unvisited = True
                    
                    if dx == 1:
                        grid[y][x].walls["right"] = False
                        grid[ny][nx].walls["left"] = False
                    elif dx == -1:
                        grid[y][x].walls["left"] = False
                        grid[ny][nx].walls["right"] = False
                    elif dy == 1:
                        grid[y][x].walls["bottom"] = False
                        grid[ny][nx].walls["top"] = False
                    elif dy == -1:
                        grid[y][x].walls["top"] = False
                        grid[ny][nx].walls["bottom"] = False

                    stack.append((nx, ny))
                    break
            
            if not found_unvisited:
                stack.pop()
        
        return grid

    def _random_path_cell(self, grid:list, visited:set):
        """Renvoie une cellule aléatoire parmi les cellules qui ne sont pas visitées"""
        valid_cells = []
        for y, row in enumerate(grid):
            for x, _ in enumerate(row):
                if (x,y) not in visited:
                    valid_cells.append((x, y))
        return random.choice(valid_cells) if valid_cells else (0, 0)
    

    def draw(self, surface:pygame.Surface):
        """
        Affichage de la map pour le débogage sur la Surface donnée
        """
        w, h = surface.get_size()
        cell_size_x, cell_size_y = w // self.width, h // self.height
        surface.fill((0,0,0))

        for y in range(self.height):
            for x in range(self.width): 
                self.draw_cell(x, y, (cell_size_x, cell_size_y), surface)

    def draw_cell(self, x, y, cell_size, surface):
        """Affiche la salle correspondante | Composant de `draw`"""
        if type(cell_size) is int:
            cell_size_x, cell_size_y = cell_size, cell_size
        else:
            cell_size_x, cell_size_y = cell_size
        room = self.map[y][x]
        color = (0, 0, 0)

        px = x * cell_size_x
        py = y * cell_size_y

        pygame.draw.rect(surface, color, (px, py, cell_size_x, cell_size_y))

        wall_thickness = 2
        wall_color = (255, 255, 255)

        if room.walls["top"]:
            pygame.draw.line(surface, wall_color, (px, py), (px + cell_size_x, py), wall_thickness)
        if room.walls["bottom"]:
            pygame.draw.line(surface, wall_color, (px, py + cell_size_y), (px + cell_size_x, py + cell_size_y), wall_thickness)
        if room.walls["left"]:
            pygame.draw.line(surface, wall_color, (px, py), (px, py + cell_size_y), wall_thickness)
        if room.walls["right"]:
            pygame.draw.line(surface, wall_color, (px + cell_size_x, py), (px + cell_size_x, py + cell_size_y), wall_thickness)

    def create_image(self, filename: str = "assets/map.png", cell_size: int = 30):
        """
        Crée une image PNG de la map sans ouvrir de fenêtre.

        Parameters
        ----------
        filename:str
            chemin de sortie
        cell_size: int
            taille en pixels d'une cellule
        """
        pygame.init()
        width_px = cell_size * self.width
        height_px = cell_size * self.height
        surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)

        for y in range(self.height):
            for x in range(self.width):
                self.draw_cell(x, y, cell_size, surface)

        try:
            pygame.image.save(surface, filename)
        except Exception as e:
            pygame.quit()
            print(e)
            raise

        pygame.quit()