import pygame

from domain.models.weapon import Weapon

class Pistol(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.reload_frames = []
        """The animation frames of this weapon when reloading."""
        
    
    def fire_anim(self):
        _still_firing = True
        self.firing_frame += 0.1
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            _still_firing = False
        self.image = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.image = pygame.transform.flip(self.image, False, True)
        return _still_firing
    
    def reload_anim(self):
        pass