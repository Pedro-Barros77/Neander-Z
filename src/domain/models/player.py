import pygame

from domain.utils import colors, constants
from domain.services import game_controller
from pygame.math import Vector2 as vec



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, **kwargs):
        super().__init__()
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.color = kwargs.pop("color", colors.GREEN)
        self.net_id = kwargs.pop("net_id", 0)
        self.jump_force = kwargs.pop("jump_force", 15)
        self.name = kwargs.pop("name", "player")
        
        self.image = game_controller.scale_image(pygame.image.load(image), 2)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)