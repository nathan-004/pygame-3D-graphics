import os
import pygame

class FrameObject:
    def __init__(self, path:str):
        """
        Parameters
        ----------
        path:str
            Chemin vers le dossier contenant les fichiers dans l'ordre alphabétique
        """
        if not os.path.isdir(path):
            raise TypeError(f"Chemin {path} non valide.")
        
        self.path = path
        self.textures_paths = [text_path for text_path in os.listdir(path) if os.path.isfile(text_path)]
        self.textures_paths.sort()

        self.current_idx = 0

    @property
    def texture(self):
        return pygame.image.load(self.textures_paths[self.current_idx])