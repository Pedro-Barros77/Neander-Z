import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.enemy import Enemy



class Zombie1(Enemy):
    def __init__(self, pos, image, **kwargs):
        super().__init__(pos, image)
        
        self.damage = kwargs.pop("damage", 5)
        self.name = kwargs.pop("name", "zombie_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_dir = self.dir.copy()