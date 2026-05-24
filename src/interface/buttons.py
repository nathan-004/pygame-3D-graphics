import pygame
import time

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
        self.states = [base]

        if hover is not None:
            self.states.append(hover)
        
        if end is not None:
            self.states.append(end)

        self.current_state = 0
        self.action = f
        
        CURRENT_BUTTONS.append(self)
    
    def tick(self, event):
        pass

    def display(self, window: pygame.Surface):
        try:
            current = self.states[self.current_state]
        except IndexError:
            current = self.states[0]
        window.blit(current.display, current.pos)

class MouseButton(Button):
    def tick(self, event):
        current = self.states[self.current_state]
        mouse_pos = pygame.mouse.get_pos()

        if (current.pos[0] <= mouse_pos[0] <= current.pos[0] + current.size[0] and 
            current.pos[1] <= mouse_pos[1] <= current.pos[1] + current.size[1]):
            self.current_state = 1
        else:
            self.current_state = 0
        
        if self.hover is not None:
            current = self.states[self.current_state]
        else:
            current = self.states[0]
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.current_state == 1:
            self.action()
            self.current_state = 2

class KeyButton(Button):
    TIME_LIMIT = 0.1

    def __init__(self, key:int, f, base, end = None):
        self.key = key
        self.last_time = 0
        super().__init__(f, base, None, end)

    def tick(self, event):
        if event.type == pygame.KEYDOWN and event.key == self.key:
            self.action()
            self.current_state = 1
            self.last_time = time.time()

    def display(self, window):
        res = super().display(window)
        if time.time() - self.last_time >= self.TIME_LIMIT:
            self.current_state = 0
        return res

def activate(button: Button):
    CURRENT_BUTTONS.append(button)

def deactivate(button: Button):
    CURRENT_BUTTONS.remove(button)