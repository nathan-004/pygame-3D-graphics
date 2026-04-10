import pygame

L = 5.0 # Longueur d'une salle
K = 0.1 # Facteur diminution intensité lumière

# Textures
WALL_TEXTURE = pygame.image.load("assets/mur_texture.jpg")
FLOOR_TEXTURE = pygame.image.load("assets/a-brown1.png")
CEILING_TEXTURE = pygame.image.load("assets/slime1.jpg")

TORCH_TEXTURE = [pygame.image.load("assets/torch.png")]*4 +[pygame.image.load("assets/torch_top.png"),
              pygame.image.load("assets/torch_bottom.png")]

DISPLAY_SIGN = pygame.image.load("assets/panneau.png")
SUPPORT_SIGN = pygame.image.load("assets/panneau_pied.png")