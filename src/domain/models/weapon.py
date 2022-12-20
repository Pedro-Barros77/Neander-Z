import pygame
import os
from os import path
from pygame.math import Vector2 as vec


from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.igravitable import IGravitable

class Weapon(pygame.sprite.Sprite):
    def __init__(self, pos, **kwargs):
        super().__init__()
        
        # The name of the object, for debugging.
        self.name = kwargs.pop("name", "weapon")
        
        self.dir: int = 0
        """The direction that this weapon is pointing to (left: -1, right: 1)."""
        self.last_dir: int = 1
        """The direction that this weapon was pointing to on the last frame (left: -1, right: 1)."""
        
        self.fire_frames = [pygame.Surface((1,1))]
        """The animation frames of this weapon when firing/attacking."""
        _path = kwargs.pop("fire_frames_path", None) 
        if _path != None:
            self.fire_frames = game_controller.load_sprites(_path)
            
        self.idle_frame = self.fire_frames[0]
        """The image of this weapon when not animating."""
            
        self.image = self.idle_frame
        """The surface of this weapon."""
        
        self.current_frame = self.idle_frame
        """The image of the current animation frame, without rotating."""
        
        self.damage = kwargs.pop("damage", 0)
        
        self.rect = self.image.get_rect()
        """The rect of this weapon."""
        self.rect.topleft = pos
        
        self.firing_frame = 0
        """The current frame of firing animation."""