import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums
from domain.services import game_controller, menu_controller

#button class
class Button(pygame.sprite.Sprite):
    def __init__(self, pos: vec, image: str, **kwargs):
        self.image = None
        self.scale = kwargs.pop("scale", 1)
        self.set_image(image)
            
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.center = self.rect.center
        
        self.name = kwargs.pop("name", "")
        self.text = kwargs.pop("text", "")
        self.visible = kwargs.pop("visible", True)
        self.text_color = kwargs.pop("text_color", colors.WHITE)
        self.text_font: pygame.font.Font = kwargs.pop("text_font", pygame.font.SysFont('arial', 30))
        self.text_surface: pygame.Surface = None
        self.hover_scale = kwargs.pop("hover_scale", 1.1)
        
        self.last_clicked = True
        self.sound_clicked = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.UI,enums.SFXActions.CLICKED, enums.SFXName.BTN_CLICK))
        self.sound_hover = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.UI,enums.SFXActions.HOVER, enums.SFXName.BTN_HOVER))
        
        
        if len(self.text) > 0:
            self.text_surface = menu_controller.get_text_surface(self.text, self.text_color, self.text_font)
        else:
            self.text_surface = pygame.Surface((0,0))
        self.start_image = self.image.copy()
        self.start_text = self.text_surface.copy()
        
        self.on_hover: function = kwargs.pop("on_hover", self.default_on_hover)
        self.on_click: function = kwargs.pop("on_click", lambda: print('clicked ' + self.text))
        
        self.enabled = kwargs.pop("enabled", True)
        if not self.enabled:
            self.enable(False)
        self.clicked = False
        self.hovered = False
        
    def set_image(self, file_path: str):
        self.image = pygame.image.load(file_path)
        if self.scale != 1:
            self.image = game_controller.scale_image(self.image, self.scale)
        self.start_image = self.image.copy()
    
    def set_text(self, txt: str):
        self.text = txt
        self.text_surface = menu_controller.get_text_surface(self.text, self.text_color, self.text_font)
        self.start_text = self.text_surface.copy()
        
    def enable(self, enabled: bool):
        self.enabled = enabled
        self.default_enable()
    
    def hide(self):
        self.visible = False
    def show(self):
        self.visible = True
        
    def default_enable(self):
        _darkness = 100
        
        if not self.enabled:
            self.image = self.start_image.copy()
            self.image.fill(colors.set_alpha(colors.BLACK, _darkness), special_flags=pygame.BLEND_RGBA_SUB)
            self.text_surface = self.start_text
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            self.image = self.start_image.copy()
            self.text_surface = self.start_text
            self.rect = self.image.get_rect()
            self.rect.center = self.center
        
    def default_on_hover(self):
        _brightness = 30
        
        if self.hovered: #hover in
            self.image.fill((_brightness, _brightness, _brightness), special_flags=pygame.BLEND_RGB_ADD)
            if self.hover_scale != 1:
                self.image = game_controller.scale_image(self.image, self.hover_scale)
                self.text_surface = game_controller.scale_image(self.text_surface, self.hover_scale)
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            self.sound_hover.play()
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: #hover out
            self.image = self.start_image.copy()
            self.text_surface = self.start_text
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
            
    def update(self, **kwargs):
        action = False
        
        if not self.visible:
            return


        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0] == 1
        
        _was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if not self.enabled:
            return
        
        if self.hovered:
            if not _was_hovered:
                self.on_hover()
            if clicked and not self.clicked and not self.last_clicked:
                self.sound_clicked.play()
                self.clicked = True
                self.on_click()
                
        elif _was_hovered:
            self.on_hover()
            
        if not clicked:
            self.clicked = False
        
        self.last_clicked = clicked
        return action
        
    
    def draw(self, surface: pygame.Surface, offset: vec = vec(0,0)):
        if not self.visible:
            return
        
        surface.blit(self.image, pygame.Rect(self.rect.topleft + offset, self.rect.size))
        
        if self.text_surface != None:
            _text_rect = self.text_surface.get_rect()
            _text_rect.center = self.rect.center
            _text_rect.topleft += offset
            surface.blit(self.text_surface, _text_rect)
            