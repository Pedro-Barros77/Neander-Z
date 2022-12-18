import pygame
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon

class Pistol(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.damage = 5
        
        self.reload_frames = []
        """The animation frames of this weapon when reloading."""
        
        self.barrel_offset = vec(0, 7)
        
    
    def fire_anim(self):
        _still_firing = True
        self.firing_frame += 0.1
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            _still_firing = False
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
        return _still_firing
    
    def reload_anim(self):
        pass