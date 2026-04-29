import os
import pygame

frame_objects = []

class FrameObject:
    def __init__(self, path:str, frames_transition:int = 2, frame_width: int = None, frame_height: int = None, frames_per_row: int = None):
        """
        Parameters
        ----------
        path:str
            Chemin vers un dossier contenant les fichiers dans l'ordre alphabétique
            OU chemin vers une sprite sheet (image avec multiple frames)
        frames_transition:int
            Nombre de frames entre chaque mise à jour
        frame_width:int
            Largeur d'un frame (pour sprite sheet uniquement)
        frame_height:int
            Hauteur d'un frame (pour sprite sheet uniquement)
        frames_per_row:int
            Nombre de frames par ligne (optionnel, calculé automatiquement si None)
        """
        self.path = path
        self.current_idx = 0
        self.frames_transition = frames_transition
        self.textures = []  # Liste des surfaces (pour sprite sheet) ou chemins (pour dossier)
        self.is_spritesheet = False
        
        # Vérifier si c'est un fichier image ou un dossier
        if os.path.isfile(path):
            self._load_spritesheet(path, frame_width, frame_height, frames_per_row)
        elif os.path.isdir(path):
            self._load_frames_from_directory(path)
        else:
            raise TypeError(f"Chemin {path} non valide (fichier ou dossier inexistant).")
    
        global frame_objects
        frame_objects.append(self)
    
    def _load_spritesheet(self, path: str, frame_width: int, frame_height: int, frames_per_row: int = None):
        """Charge une sprite sheet et découpe les frames"""
        if frame_width is None or frame_height is None:
            raise ValueError("frame_width et frame_height sont nécessaires pour une sprite sheet")
        
        spritesheet = pygame.image.load(path)
        sheet_width, sheet_height = spritesheet.get_size()
        
        # Calculer le nombre de frames
        frames_per_col = sheet_height // frame_height
        if frames_per_row is None:
            frames_per_row = sheet_width // frame_width
        
        # Découper les frames
        for row in range(frames_per_col):
            for col in range(frames_per_row):
                x = col * frame_width
                y = row * frame_height
                
                # Vérifier qu'on ne dépasse pas les limites
                if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                    frame = spritesheet.subsurface((x, y, frame_width, frame_height))
                    self.textures.append(frame.copy())
        
        self.is_spritesheet = True
    
    def _load_frames_from_directory(self, path: str):
        """Charge les frames depuis un dossier"""
        textures_paths = [os.path.join(path, text_path) for text_path in os.listdir(path) 
                         if os.path.isfile(os.path.join(path, text_path))]
        textures_paths.sort()
        self.textures = textures_paths

    @property
    def texture(self) -> pygame.Surface:
        if self.is_spritesheet:
            return self.textures[self.current_idx]
        else:
            return pygame.image.load(self.textures[self.current_idx])
    
    def tick(self, f: int):
        if f % self.frames_transition == 0:
            self.update()

    def update(self, var: int = 1):
        self.current_idx += var

        if self.current_idx >= len(self.textures):
            self.current_idx = self.current_idx % (len(self.textures) - 1)
