import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants

class Modal:
    def __init__(self, **kwargs):
        self.panel_color = kwargs.pop("panel_color", colors.set_alpha(colors.BLACK, 230))
        self.panel_margin = kwargs.pop("panel_margin", vec(50,50))
        self.border_color = kwargs.pop("border_color", colors.LIGHT_GRAY)
        self.border_width = kwargs.pop("border_width", 1)
    
    
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        self.screen = screen
        
        
        panel = pygame.Surface(vec(screen_rect.size) - self.panel_margin, pygame.SRCALPHA)
        panel.fill(self.panel_color)
        pygame.draw.rect(panel, self.border_color, panel.get_rect(), self.border_width)
       
        #black panel
        screen.blit(panel, self.panel_margin/2)


    def update(self):
        pass
        
       
            
       
            