import pygame
from pygame.math import Vector2 as vec

from domain.models.igravitable import IGravitable
from domain.utils import colors

class Rectangle(pygame.sprite.Sprite, IGravitable):
    def __init__(self, size, pos, **kwargs):
        super().__init__()
        IGravitable.__init__(self)
        
        self.size = size
        """The width and height of the surface.""" 
        
        self.pos = vec(pos)
        """The position of the top-left corner of the surface.""" 
        
        self.image = pygame.Surface(size)
        """The map image/surface.""" 
        
        self.rect = self.image.get_rect()
        """The rectangle of the image.""" 
        
        self.color = kwargs.pop("color", colors.RED)
        """The color to fill the rectangle."""        
        self.image.fill(self.color)
        
        self.name = kwargs.pop("name", "rectangle")
        """The name of this object. For debugging purposes."""        
        
        self.gravity_enabled = kwargs.pop("gravity_enabled", False)
        """If this object should be affected by the gravity.""" 
        
        self.collision_enabled = kwargs.pop("collision_enabled", False)
        """If this object should collide with other objects.""" 
        	
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
    def update_rect(self):
        self.rect.topleft = self.pos
        
    def update_pos(self):
        self.pos = self.rect.topleft