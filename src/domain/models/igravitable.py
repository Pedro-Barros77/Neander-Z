from pygame.math import Vector2 as vec
import pygame

class IGravitable:
    """Objects that are affected by the gravity.
    """
    instances = []
    def __init__(self):
        self.__class__.instances.append(self)
        
    
    speed: vec = vec(0,0)
    acceleration: vec = vec(0,0)
    
    size = (10,10)
    rect = pygame.Rect((0,0), size)
    last_rect = rect.copy()
    gravity_scale = 1
    
    gravity_enabled = True
    collision_enabled = True