import pygame, math, random
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants, math_utillity as maths
from domain.services import game_controller, menu_controller as mc, resources
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos: vec, angle: float, speed: float, damage: float, owner:int, id: int, **kwargs):
        super().__init__()
        
        self.id = id
        self.owner = owner
        self.bullet_type = kwargs.pop("bullet_type", enums.BulletType.PISTOL)
        self.image_scale = kwargs.pop("image_scale", 1)
        self.image = game_controller.scale_image(pygame.image.load(resources.get_bullet_path(self.bullet_type)), self.image_scale, enums.ConvertType.CONVERT_ALPHA)
        self.current_frame: pygame.Surface = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.angle = angle
        self.speed = speed
        self.collision_groups = game_controller.bullet_target_groups
        self.damage = damage
        self.total_damage = damage
        self.owner_offset = vec(0,0)
        self.is_alive = True
        self.start_pos = pos
        self.tail_hitbox: Rectangle = self.get_tail()
        self.pierce_damage_multiplier = kwargs.pop("pierce_damage_multiplier", 1)
        self.pierce_count = 0
        self.max_pierce_targets = kwargs.pop("max_pierce_targets", 1)
        self.hit_targets: list[int] = []
        
        self.hit_callback: function = kwargs.pop("hit_callback", lambda s: None)
        
        self.max_range = kwargs.pop("max_range", 0)
        self.min_range = kwargs.pop("min_range", 0)
        
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 0)
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 0)
        
        self.explosion_frame = 0
        self.exploding = False
        if self.explosion_max_radius > 0:
            self.explosion_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\explosion_01', convert_type=enums.ConvertType.CONVERT_ALPHA)
            self.explosion_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.HIT) + f'0{i}.mp3') for i in range(1,4)]
            for s in self.explosion_sounds:
                s.set_volume(0.3)
            
    def explosion_sound(self):
        sound = self.explosion_sounds[random.randint(0, len(self.explosion_sounds)-1)]

        sound.play()
        
    def get_tail(self):
        _tail_rect = self.rect.copy()
        _tail_rect.width = self.rect.width * self.speed/2
        if self.image_scale != 1:
            _tail_rect.width *= self.image_scale-1
        
        if abs(self.angle) < 90:
            _tail_rect.topright = self.rect.topright
        else:
            _tail_rect.topleft = self.rect.topleft
            
        
        
        if self.start_pos.x > _tail_rect.x and abs(self.angle) < 90:
            _tail_rect.width -= abs(self.start_pos.x - _tail_rect.left)
            _tail_rect.topright = self.rect.topright
        elif self.start_pos.x < _tail_rect.x and abs(self.angle) > 90:
            _tail_rect.width -= abs(_tail_rect.right - (self.start_pos.x + self.rect.width))
            _tail_rect.topleft = self.rect.topleft
        _tail_rect.width = abs(_tail_rect.width)
        _rec = Rectangle(_tail_rect.size, _tail_rect.topleft)
        return _rec
    
    def draw(self, screen: pygame.Surface, offset: vec):
        if not self.is_alive:
            return    
        
        if self.exploding:
            self.image = self.current_frame.copy()
        
        screen.blit(self.image, vec(self.rect.topleft) - offset)
        
        # pygame.draw.circle(screen, colors.RED, self.rect.center - offset, self.explosion_min_radius, 2)
        
        # pygame.draw.rect(screen, colors.RED, ((self.tail_hitbox.rect.topleft) - offset, self.tail_hitbox.rect.size), 2)
        
    def update(self, **kwargs):
        if not self.is_alive:
            return
        
        if self.exploding:
            self.explosion_anim(0.5)
            return
        
        if self.max_range > 0:
            _distance = vec(self.rect.topleft).distance_to(vec(self.start_pos))
            if _distance >= self.max_range:
                self.destroy()
            if self.min_range > 0 and _distance > self.min_range:
                _diff = _distance - self.min_range
                _range = self.max_range - self.min_range
                
                _percentage = (_diff * 100 / _range) / 100
                
                self.damage = self.total_damage - (_percentage * self.total_damage)
        
        _new_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), self.speed * mc.dt, -math.radians(self.angle))
        self.image, self.rect = game_controller.rotate_to_angle(self.current_frame, _new_pos, self.angle)
        
        # if will be out of the map bounds
        if _new_pos.x > game_controller.map_size.x or _new_pos.x < 0 or\
            _new_pos.y > game_controller.map_size.y or _new_pos.y < 0:
            self.kill()
        
        # movement
        self.rect.topleft = _new_pos
        collided = self.bullet_collision()
        
        if collided:
            if self.explosion_min_radius > 0:
                for group in self.collision_groups:
                    _explosion_min_hitbox = Rectangle((self.explosion_min_radius*2, self.explosion_min_radius*2), vec(self.rect.topleft), radius = self.explosion_min_radius)
                    _explosion_min_hitbox.rect.center = self.rect.center
                    _explosion_max_hitbox = Rectangle((self.explosion_max_radius*2, self.explosion_max_radius*2), vec(self.rect.topleft), radius = self.explosion_max_radius)
                    _explosion_max_hitbox.rect.center = self.rect.center
                    
                    collided_explosion = pygame.sprite.spritecollide(_explosion_max_hitbox, group, False, pygame.sprite.collide_circle)
                    for c in collided_explosion:
                        if isinstance(c, Enemy) or isinstance(c, Rectangle) and c.name == "zombie_body":
                            
                            
                            _distance = vec(self.rect.center).distance_to(c.rect.center)
                            if _distance >= self.explosion_max_radius:
                                break
                            if _distance > self.explosion_min_radius:
                                _diff = _distance - self.explosion_min_radius
                                _range = self.explosion_max_radius - self.explosion_min_radius
                                
                                _percentage = (_diff * 100 / _range) / 100
                                
                                self.damage = self.total_damage - (_percentage * self.total_damage)
                            
                            c.take_damage(self.damage, self.owner)
                            
            self.hit_callback(self)
            if self.pierce_damage_multiplier == 1:
                self.destroy()
            else:
                self.damage *= self.pierce_damage_multiplier
                self.pierce_count += 1
                if self.pierce_count >= self.max_pierce_targets:
                    self.destroy()
        self.rect.topleft = _new_pos
        self.tail_hitbox = self.get_tail()
        
    
    def explosion_anim(self, speed: float):
        self.explosion_frame += speed
        
        if self.explosion_frame > len(self.explosion_frames)-1:
            self.explosion_frame = 0
            self.exploding = False
            self.kill()
        else:
            self.current_frame = self.explosion_frames[int(self.explosion_frame)]
            _rect = self.current_frame.get_rect()
            _rect.center = self.rect.center
            self.rect = _rect
            
    
    def destroy(self):
        if self.explosion_min_radius > 0:
            self.explosion_sound()
            self.exploding = True
        else:
            self.kill()
    
    def kill(self):
        self.is_alive = False
        super().kill()
    
    def bullet_collision(self):
        _collided = False
        for group in self.collision_groups:
            collisions = pygame.sprite.spritecollide(self.tail_hitbox, group, False)
            for c in collisions:
                if c.id in self.hit_targets:
                    continue
                if isinstance(c, Enemy) or isinstance(c, Rectangle):
                    c.take_damage(self.damage, self.owner)
                _collided = True
                if self.pierce_damage_multiplier == 1:
                    return _collided
                self.hit_targets.append(c.id)
        return _collided
    
    def get_netdata(self):
        values = {
            "id": self.id,
            "owner": self.owner,
            "angle": self.angle,
            "rect": tuple([*self.rect.topleft, *self.rect.size]),
            "speed": self.speed,
            "damage": self.damage,
            "bullet_type": str(self.bullet_type.name),
        }
        return values
    
    def load_netdata(self, data: dict):
        self.rect = pygame.Rect(data.pop("rect", (0,0, 1,1)))
        self.bullet_type = enums.BulletType[data.pop('bullet_type', enums.BulletType.PISTOL)]
        
        for item, value in data.items():
            setattr(self, item, value)