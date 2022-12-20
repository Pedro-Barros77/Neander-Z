import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors
from domain.services import game_controller, menu_controller

#button class
class Button(pygame.sprite.Sprite):
    def __init__(self, pos: vec, image: str, **kwargs):
        self.image = pygame.image.load(image)
        scale = kwargs.pop("scale", 1)
        if scale != 1:
            self.image = game_controller.scale_image(self.image, scale)
            
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.center = self.rect.center
        
        self.text = kwargs.pop("text", "")
        self.text_color = kwargs.pop("text_color", colors.WHITE)
        self.text_font: pygame.font.Font = kwargs.pop("text_font", pygame.font.SysFont('arial', 30))
        self.text_surface: pygame.Surface = None
        
        self.last_clicked = True
        
        if len(self.text) > 0:
            self.text_surface = menu_controller.get_text_surface(self.text, self.text_color, self.text_font)
        else:
            self.text_surface = pygame.Surface((0,0))
        self.start_image = self.image.copy()
        self.start_text = self.text_surface.copy()
        
        self.on_hover: function = kwargs.pop("on_hover", self.default_on_hover)
        self.on_click: function = kwargs.pop("on_click", lambda: print('clicked ' + self.text))
        
        self.clicked = False
        self.hovered = False
        
    def default_on_hover(self):
        _brightness = 30
        _scale = 1.1
        
        if self.hovered: #hover in
            self.image.fill((_brightness, _brightness, _brightness), special_flags=pygame.BLEND_RGB_ADD)
            self.image = game_controller.scale_image(self.image, _scale)
            self.text_surface = game_controller.scale_image(self.text_surface, _scale)
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: #hover out
            self.image = self.start_image.copy()
            self.text_surface = self.start_text
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
            
    def update(self, **kwargs):
        action = False

        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0] == 1
        
        _was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            if not _was_hovered:
                self.on_hover()
            if clicked and not self.clicked and not self.last_clicked:
                self.clicked = True
                self.on_click()
        elif _was_hovered:
            self.on_hover()
            
        if not clicked:
            self.clicked = False
        
        self.last_clicked = clicked
        return action
        
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
        
        if self.text_surface != None:
            _text_rect = self.text_surface.get_rect()
            _text_rect.center = self.rect.center
            surface.blit(self.text_surface, _text_rect)