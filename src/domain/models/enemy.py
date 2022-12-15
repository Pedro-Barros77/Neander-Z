import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.igravitable import IGravitable



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        
        self.name = "enemy"
        self.jump_force = 12
        self.damage = 1
        
        self.pos: vec = vec((pos))
        self.speed = vec(0,0)
        self.acceleration: vec = vec(0,0)
        self.dir: vec = vec(0,0)
        self.last_dir: vec = self.dir.copy()
        
        self.image = game_controller.scale_image(pygame.image.load(image), 2)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)