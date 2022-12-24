import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums
from domain.services import game_controller
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle




class ZRoger(Enemy):
    def __init__(self, pos, enemy_name,wave, **kwargs):
        super().__init__(pos, enemy_name,wave, **kwargs)
        
        self.damage = kwargs.pop("damage", 5)
        self.name = kwargs.pop("name", f"zombie_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", 30)
        self.hit_frame = 8
        self.hiting = False
        self.attack_box = vec(15,15)
        self.hit_rectangle = None
 
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.running:
            self.run_anim(abs(self.speed.x / 5))
        
        if self.attacking:
            self.attcking_anim(0.2)

    def attack(self):
        self.hiting = True
        self.hit_rectangle = Rectangle(self.attack_box, vec(self.rect.center) + vec(20 * self.dir.x,-20) )
       
        collided = self.attack_collision(self.hit_rectangle)
        if len(collided) > 0:
            for c in collided:
                c.take_damage(self.damage)
            
        
    def run_anim(self, speed: float):
        self.run_frame += speed
        if self.run_frame > len(self.run_frames)-1:
            self.run_frame = 0
        self.image = game_controller.scale_image(self.run_frames[int(self.run_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attcking_anim(self, speed: float):
        self.attack_frame += speed
        if int(self.attack_frame) == self.hit_frame - 1 and not self.hiting:
            self.attack()
        if self.attack_frame > len(self.attack_frames)-1:
            self.attack_frame = 0
            self.attacking = False
            self.hiting = False
        self.image = game_controller.scale_image(self.attack_frames[int(self.attack_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    
    def draw(self, surface: pygame.Surface, offset: vec):
        super().draw(surface, offset)
        