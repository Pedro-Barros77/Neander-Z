import pygame, datetime
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
        self.head_shot_multiplier = 2
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True))
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width, self.hitbox_head.rect.height - self.rect.height/1.5)))
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False))
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width, self.hitbox_body.rect.height - self.hitbox_head.rect.height)))
 
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.running and self.death_time == None:
            self.run_anim(abs(self.speed.x / 5))
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2)
        
        if self.dying and self.death_time == None:
            self.dying_anim(0.2)
            


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
    
    def dying_anim(self, speed: float):
        self.death_frame += speed
        if self.death_frame > len(self.death_frames)-1:
            self.death_time = datetime.datetime.now()
            self.death_frame = 0
        else:
            self.image = game_controller.scale_image(self.death_frames[int(self.death_frame)], self.image_scale)
        if self.acceleration.x > 0 and self.death_time == None:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
        