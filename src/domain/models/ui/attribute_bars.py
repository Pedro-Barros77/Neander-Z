import pygame
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller
from domain.utils import colors, constants, enums, math_utillity as math

class AttributeBar:
    def __init__(self, rect: pygame.Rect, **kwargs):
        
        #properties
        self.rect = rect
        self.max_value = kwargs.pop("max_value", 1)
        self.value = kwargs.pop("value", 0)
        self.upgrade_value = kwargs.pop("upgrade_value", 0)
        self.downgrade_value = kwargs.pop("downgrade_value", 0)
        self.bars_count = kwargs.pop("bars_count", 5)
        
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        
        #style
        self.bar_fill_color = kwargs.pop("bar_fill_color", colors.LIGHT_GRAY)
        self.bar_background_color = kwargs.pop("bar_background_color", colors.BLACK)
        self.bar_upgrade_fill_color = kwargs.pop("bar_upgrade_fill_color", colors.YELLOW)
        self.bar_downgrade_fill_color = kwargs.pop("bar_downgrade_fill_color", colors.RED)
        self.bar_border_color = kwargs.pop("bar_border_color", colors.WHITE)
        self.bar_border_width = kwargs.pop("bar_border_width", 1)
        self.bar_border_radius = kwargs.pop("bar_border_radius", 5)
        
        self.bars_margin = kwargs.pop("bars_margin", 5)
        self.bar_size: vec = kwargs.pop("bar_size", vec(self.rect.width/self.bars_count - self.bars_margin, self.rect.height))
        
        self.rerender()
        
    def add_value(self, steps = 1):
        self.value += steps * (self.max_value / self.bars_count)
        self.value = math.clamp(self.value, 0, self.max_value)
        self.rerender()
        
    def remove_value(self, steps = 1):
        self.value -= steps * (self.max_value / self.bars_count)
        self.value = math.clamp(self.value, 0, self.max_value)
        self.rerender()
        
    def rerender(self):
        _value_step = self.max_value / self.bars_count
        
        for b in range(self.bars_count):
            _fill_color = None
            _fill_half = False
            _bar_rect = pygame.Rect((self.bars_margin/2 + b * (self.bar_size.x + self.bars_margin), 0), self.bar_size)
            
            if (self.downgrade_value * _value_step) + self.value >= _value_step * (b+1): #fill downgrade
                _fill_color = self.bar_downgrade_fill_color
                pygame.draw.rect(self.image, _fill_color, _bar_rect, border_radius = self.bar_border_radius)
            elif (self.upgrade_value * _value_step) + self.value >= _value_step * (b+1): #fill upgrade
                _fill_color = self.bar_upgrade_fill_color
                pygame.draw.rect(self.image, _fill_color, _bar_rect, border_radius = self.bar_border_radius)
            else: #fill background
                _fill_color = self.bar_background_color
                
            if self.value >= _value_step * (b+1): #fill value
                _fill_color = self.bar_fill_color
            elif self.value < _value_step * (b+1) and self.value >= (_value_step * (b)) + _value_step/2: #fill half value
                _fill_color = self.bar_fill_color
                _fill_half = True
                
            
                
            if _fill_half:
                _half_bar_rect = _bar_rect.copy()
                _half_bar_rect.width /= 2
                pygame.draw.rect(self.image, _fill_color, _half_bar_rect, border_radius= self.bar_border_radius)
            else:
                pygame.draw.rect(self.image, _fill_color, _bar_rect, border_radius= self.bar_border_radius)
            pygame.draw.rect(self.image, self.bar_border_color, _bar_rect, self.bar_border_width, self.bar_border_radius)
            
        
        
    def update(self, offset: vec = vec(0,0)):
        pass
    
    def draw(self, screen: pygame.Surface, offset: vec = vec(0,0)):
        screen.blit(self.image, math.rect_offset(self.rect, offset))
        
        
    