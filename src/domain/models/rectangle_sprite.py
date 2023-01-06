import pygame
from pygame.math import Vector2 as vec

from domain.models.igravitable import IGravitable
from domain.utils import colors

class Rectangle(pygame.sprite.Sprite, IGravitable):
    def __init__(self, size, pos, **kwargs):
        super().__init__()
        IGravitable.__init__(self)
        
        self.pos = vec(pos)
        """The position of the top-left corner of the surface.""" 
        
        self.id = kwargs.pop("id", 0)
        """The id of this rectangle.""" 
        
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        """The map image/surface.""" 
        
        self.rect = self.image.get_rect()
        """The rectangle of the image.""" 
        
        self.color = kwargs.pop("color", colors.set_alpha(colors.WHITE, 0))
        """The color to fill the rectangle."""        
        
        self.border_color = kwargs.pop("border_color", colors.RED)
        """The color to fill the border of the rectangle."""        
        
        self.border_width = kwargs.pop("border_width", 1)
        """The width of the rectangle's border."""        
        
        self.border_radius = kwargs.pop("border_radius", 0)
        """The radius of the rectangle's border."""        
        
        self.name = kwargs.pop("name", "rectangle")
        """The name of this object. For debugging purposes."""        
        
        self.gravity_enabled = kwargs.pop("gravity_enabled", False)
        """If this object should be affected by the gravity.""" 
        
        self.collision_enabled = kwargs.pop("collision_enabled", False)
        """If this object should collide with other objects.""" 
        
        self.take_damage_callback = kwargs.pop("take_damage_callback", lambda value, attacker: None)
        """The function to be called when take_damage is called.""" 
        
        self.get_health_callback = kwargs.pop("get_health_callback", lambda value: None)
        """The function to be called when get_health is called.""" 
        
        self.radius = kwargs.pop("radius", 0)
        
        	
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
        self.rerender()
        
    def update_rect(self):
        self.rect.topleft = self.pos
        
    def update_pos(self):
        self.pos = self.rect.topleft
        
    def set_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.rerender()
        
    def rerender(self):
        self.image.fill(self.color)
        pygame.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width, self.border_radius)
        
    def draw(self, surface: pygame.Surface, offset: vec):
        surface.blit(self.image, self.rect.topleft - offset)
        
    def take_damage(self, value: float, attacker = None):
        self.take_damage_callback(value, attacker)
    
    def get_health(self, value: float):
        self.get_health_callback(value)