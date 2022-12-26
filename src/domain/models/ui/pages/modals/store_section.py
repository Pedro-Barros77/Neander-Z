import pygame
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants
from domain.models.ui.button import Button
from domain.models.ui.pages.modals.modal import Modal

class Store:
    def __init__(self, player, **kwargs):
        
        self.player = player

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        
        store_title = menu_controller.get_text_surface("Store", colors.WHITE, self.font(50))        
        screen.blit(store_title, (110,110))
        

    def update(self):
        pass
            
    def blit_debug(self, screen, **kwargs):
        pass
       
            
       
            