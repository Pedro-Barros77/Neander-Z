import pygame
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants, enums
from domain.models.ui.button import Button
from domain.models.ui.scrollbar import ScrollBar
from domain.models.ui.pages.modals.modal import Modal

class Store:
    def __init__(self, player, panel_margin: vec, **kwargs):
        
        self.player = player
        self.panel_margin = panel_margin
        self.store_v_scrollbar: ScrollBar = None
        self.weapons_h_scrollbar: ScrollBar = None
        self.image: pygame.Surface = None

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def update(self, **kwargs):
        events = kwargs.pop("events", [])
        
        for e in events:
            if self.store_v_scrollbar != None:
                self.store_v_scrollbar.event_handler(e)
                self.store_v_scrollbar.update()
            if self.weapons_h_scrollbar != None:
                pass
                self.weapons_h_scrollbar.event_handler(e)
                self.weapons_h_scrollbar.update()
                
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        if self.image == None:
            self.image = pygame.Surface(screen_rect.size - self.panel_margin, pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        image_rect = self.image.get_rect()
        image_rect.topleft = self.panel_margin/2
        
        if self.store_v_scrollbar == None:
            self.store_v_scrollbar = ScrollBar(enums.Orientation.VERTICAL, vec(1,(screen_rect.height-self.panel_margin.y) *2), pygame.Rect((screen_rect.width - self.panel_margin.x, self.panel_margin.y), (20,screen_rect.height - self.panel_margin.y*2)))
        if self.weapons_h_scrollbar == None:
            self.weapons_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec((screen_rect.width-self.panel_margin.x)*2,1), pygame.Rect((self.panel_margin.x, screen_rect.height - self.panel_margin.y), (screen_rect.width - self.panel_margin.x*2, 20)), visible = False)
        
        store_title = menu_controller.get_text_surface("Store", colors.WHITE, self.font(50))     
        
        [self.image.blit(store_title, (110, (110* i) + self.store_v_scrollbar.scroll_offset.y)) for i in range(1,10)]
        self.store_v_scrollbar.draw(screen)
        self.weapons_h_scrollbar.draw(screen)
        
        screen.blit(self.image, image_rect)

        
                    
    def blit_debug(self, screen, **kwargs):
        pass
       
            
       
            