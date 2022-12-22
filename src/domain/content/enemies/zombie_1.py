import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.enemy import Enemy



class Zombie1(Enemy):
    def __init__(self, pos, enemy_name, **kwargs):
        super().__init__(pos, enemy_name, **kwargs)
        
        self.damage = kwargs.pop("damage", 5)
        self.name = kwargs.pop("name", "zombie_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_dir = self.dir.copy()
        
    def update(self, **kwargs):
        self.health_bar.update()
        
        if self.running:
            self.run_anim(abs(self.speed.x / 5))
        
    def run_anim(self, speed: float):
        self.running_frame += speed
        if self.running_frame > len(self.run_frames)-1:
            self.running_frame = 0
        self.image = game_controller.scale_image(self.run_frames[int(self.running_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)