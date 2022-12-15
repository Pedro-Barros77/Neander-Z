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
        
        self.fire_frames = []
        self.reload_frames = []
        
        self.current_frame = 0
        self.firing = False
        
    def load_sprites(self, folder_path: str):
        _path = constants.ROOT_PATH + folder_path
        if not path.exists(_path):
            return
        
        images = [pygame.image.load(_path + "\\" + img) for img in os.listdir(_path) if img.endswith('.png')]
        return images
            
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