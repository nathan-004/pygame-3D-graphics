import pygame

from typing import Callable

CURRENT_BUTTONS = []

class ButtonDescriptor:
    def __init__(self, display: pygame.Surface, pos: tuple):
        """
        Parameters
        ----------
        display: pygame.Surface
            Surface à afficher
        size: tuple[width, height]
        pos: tuple[x, y]
            Position du top left corner
        """
        self.display = display
        self.size = display.get_size()
        self.pos = pos

class Button:
    def __init__(self, f:Callable, base: ButtonDescriptor, hover: ButtonDescriptor | None = None, end: ButtonDescriptor | None = None):
        self.base = base
        self.hover = hover
        self.end = end
        self.states = [base, hover, end]

        self.current_state = 0
        self.action = f
        
        CURRENT_BUTTONS.append(self)
    
    def tick(self, event):
        current = self.states[self.current_state]
        mouse_pos = pygame.mouse.get_pos()

        if (current.pos[0] <= mouse_pos[0] <= current.pos[0] + current.size[0] and 
            current.pos[1] <= mouse_pos[1] <= current.pos[1] + current.size[1]):
            self.current_state = 1
        else:
            self.current_state = 0
        
        current = self.states[self.current_state]
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.current_state == 1:
            self.action()
            self.current_state = 2

    def display(self, window):
        current = self.states[self.current_state]
        window.blit(current.display, current.pos)

def activate(button: Button):
    CURRENT_BUTTONS.append(button)

def deactivate(button: Button):
    CURRENT_BUTTONS.remove(button)