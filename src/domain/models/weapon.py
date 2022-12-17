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
        
        self.name = kwargs.pop("name", "weapon")
        
        self.pos: vec = vec((pos))
        self.dir: vec = vec(0,0)
        self.last_dir: vec = self.dir.copy()
        
        self.image = pygame.Surface(self.pos)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        
        self.fire_frames = [pygame.Surface((1,1))]
        _path = kwargs.pop("fire_frames_path", None) 
        if _path != None:
            self.fire_frames = game_controller.load_sprites(_path)
            
        self.image = self.fire_frames[0]
        self.rect = self.fire_frames[0].get_rect()
        
        self.reload_frames = []
        
        self.current_frame = 0
        self.firing = False
        
    def update(self):
        self.fire_anim()
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
        
    def fire_anim(self):
        if not self.firing: 
            return
        self.current_frame += 0.1
        
        if self.current_frame > len(self.fire_frames)-1:
            self.current_frame = 0
            self.firing = False
        self.image = self.fire_frames[int(self.current_frame)]
        
        if self.dir.x < 0:
            self.image = pygame.transform.flip(self.image, False, True)
    
    def reload_anim(self):
        pass