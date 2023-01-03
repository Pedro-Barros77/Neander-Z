import pygame, math
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants
from domain.services import game_controller, menu_controller as mc
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle

class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, pos: vec, angle: float, speed: float, damage: float, owner:int, id: int, **kwargs):
        super().__init__()
        
        self.id = id
        self.owner = owner
        self.image = game_controller.scale_image(pygame.image.load(constants.SMALL_BULLET), 1, enums.ConvertType.CONVERT_ALPHA)
        self.start_image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.angle = angle
        self.speed = speed
        self.collision_groups = game_controller.bullet_target_groups
        self.damage = damage
        self.total_damage = damage
        self.bullet_name = enums.Bullets.SMALL_BULLET
        self.owner_offset = vec(0,0)
        self.is_alive = True
        self.start_pos = pos
        self.tail_hitbox: Rectangle = self.get_tail()
        
        
        self.max_range = kwargs.pop("max_range", 0)
        self.min_range = kwargs.pop("min_range", 0)
        
    def get_tail(self):
        _tail_rect = self.rect.copy()
        _tail_rect.width = self.rect.width * 15
        _tail_rect.topright = self.rect.topright
        
        if self.start_pos.x > _tail_rect.x and abs(self.angle) < 90:
            _tail_rect.width -= abs(self.start_pos.x - _tail_rect.left)
            _tail_rect.topright = self.rect.topright
        elif self.start_pos.x < _tail_rect.x and abs(self.angle) > 90:
            _tail_rect.width -= abs(_tail_rect.right - (self.start_pos.x + self.rect.width))
            _tail_rect.topleft = self.rect.topleft
            
        _rec = Rectangle(_tail_rect.size, _tail_rect.topleft)
        return _rec
    
    def draw(self, screen: pygame.Surface, offset: vec):
        if not self.is_alive:
            return
        screen.blit(self.image, vec(self.rect.topleft) - offset)
        
        # pygame.draw.rect(screen, colors.RED, ((self.tail_hitbox.rect.topleft) - offset, self.tail_hitbox.rect.size), 2)
        
    def update(self, **kwargs):
        if not self.is_alive:
            return
        
        if self.max_range > 0:
            _distance = vec(self.rect.topleft).distance_to(vec(self.start_pos))
            if _distance >= self.max_range:
                self.kill()
            if self.min_range > 0 and _distance > self.min_range:
                _diff = _distance - self.min_range
                _range = self.max_range - self.min_range
                
                _percentage = (_diff * 100 / _range) / 100
                
                self.damage = self.total_damage - (_percentage * self.total_damage)
        
        _new_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), self.speed * mc.dt, -math.radians(self.angle))# * mc.dt
        self.image, self.rect = game_controller.rotate_to_angle(self.start_image, _new_pos, self.angle)
        
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
        self.tail_hitbox = self.get_tail()
    
    def kill(self):
        self.is_alive = False
        super().kill()
    
    def bullet_collision(self):
        for group in self.collision_groups:
            collisions = pygame.sprite.spritecollide(self.tail_hitbox, group, False)
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