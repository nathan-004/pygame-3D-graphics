import pygame

def get_bar(value: float, max_value: float, background_color: tuple, fill_color: tuple, size=(10, 1)) -> pygame.Surface:
    background = pygame.Surface(size)
    background.fill(background_color)

    pygame.draw.rect(background, fill_color, (0, 0, size[0] * value / max_value, size[1]))

    return background