import pygame, math
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants
from domain.services import game_controller
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle

class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, pos: vec, angle: float, speed: float, damage: float, owner:int, id: int, **kwargs):
        super().__init__()
        
        self.id = id
        self.owner = owner
        self.image = pygame.image.load(constants.SMALL_BULLET).convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.angle = angle
        self.speed = speed
        self.collision_groups = game_controller.bullet_target_groups
        self.damage = damage
        self.bullet_name = enums.Bullets.SMALL_BULLET
        self.owner_offset = vec(0,0)
        self.is_alive = True
        
        
    
    def draw(self, screen: pygame.Surface, offset: vec):
        if not self.is_alive:
            return
        screen.blit(self.image, vec(self.rect.topleft) - offset)
        
    def update(self, **kwargs):
        if not self.is_alive:
            return
        
        _new_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), self.speed, -math.radians(self.angle))
        
        # if will be out of the map bounds
        if _new_pos.x > game_controller.map_size.x or _new_pos.x < 0 or\
            _new_pos.y > game_controller.map_size.y or _new_pos.y < 0:
            self.kill()
        
        # movement
        self.rect.topleft = _new_pos
        collided = self.bullet_collision()
        if collided:
            self.kill()
        self.rect.topleft = _new_pos
    
    def kill(self):
        self.is_alive = False
        super().kill()
    
    def bullet_collision(self):
        for group in self.collision_groups:
            collisions = pygame.sprite.spritecollide(self, group, False)
            for c in collisions:
                if isinstance(c, Enemy) or isinstance(c, Rectangle):
                    c.take_damage(self.damage, self.owner)
                return True
        return False
    
    def get_netdata(self):
        values = {
            "id": self.id,
            "owner": self.owner,
            "angle": self.angle,
            "rect": tuple([*self.rect.topleft, *self.rect.size]),
            "speed": self.speed,
            "damage": self.damage,
            "bullet_name": str(self.bullet_name.name),
        }
        return values
    
    def load_netdata(self, data: dict):
        self.rect = pygame.Rect(data.pop("rect", (0,0, 1,1)))
        self.bullet_name = enums.Bullets[data.pop('bullet_name', enums.Bullets.SMALL_BULLET)]
        
        for item, value in data.items():
            setattr(self, item, value)