import pygame, math
from pygame.math import Vector2 as vec

from domain.utils import colors
from domain.services import game_controller
from domain.models.enemy import Enemy

class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, image_path: str, pos: vec, angle: float, speed: float, damage: float):
        
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.angle = angle
        self.speed = speed
        self.collision_groups = game_controller.bullet_groups
        self.damage = damage
        
    
    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        
    def move(self, offset: vec):
        _new_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), self.speed, -math.radians(self.angle))
        
        if _new_pos.x > game_controller.map_size.x or _new_pos.x < 0 or\
            _new_pos.y > game_controller.map_size.y or _new_pos.y < 0:
            return True
        
        
        self.rect.topleft = _new_pos + offset
        collided = self.bullet_collision()
        self.rect.topleft = _new_pos
        if collided:
            return True
        
        return False
    
    
    def bullet_collision(self):
        for group in self.collision_groups:
            collisions = pygame.sprite.spritecollide(self, group, False)
            for c in collisions:
                if isinstance(c, Enemy):
                    c.take_damage(self.damage)
            if collisions:
                return True
        return False