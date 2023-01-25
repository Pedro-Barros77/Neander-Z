import pygame, math, random, datetime
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants, math_utillity as maths
from domain.services import game_controller, menu_controller as mc, resources
from domain.models.enemy import Enemy
from domain.models.igravitable import IGravitable
from domain.models.rectangle_sprite import Rectangle

class Charge(pygame.sprite.Sprite):
    def __init__(self, pos: vec, angle: float, bullet_speed: float, damage: float, owner:int, id: int, **kwargs):
        super().__init__()
        
        self.id = id
        self.owner = owner
        self.name = kwargs.pop("name", "grenade_01")
        self.charge_type = kwargs.pop("charge_type", enums.Throwables.FRAG_GRENADE)
        self.image_scale = kwargs.pop("image_scale", 1)
        self.gravity_scale = kwargs.pop("gravity_scale", 1)
        self.fuse_timeout_ms = kwargs.pop("fuse_timeout_ms", 3000)
        self.detonate_on_impact = kwargs.pop("detonate_on_impact", True)
        self.bounciness_multiplier = kwargs.pop("bounciness_multiplier", 0.5)
        self.friction_multiplier = kwargs.pop("friction_multiplier", 0.2)
        self.rotation_speed = kwargs.pop("rotation_speed", 5)
        self.image = game_controller.load_sprites(resources.get_weapon_path(enums.Throwables.FRAG_GRENADE, enums.AnimActions.SHOOT), self.image_scale, enums.ConvertType.CONVERT_ALPHA)[0]
        self.current_frame: pygame.Surface = self.image.copy()
        self.rect = self.image.get_rect()
        self.last_rect = self.rect.copy()
        self.pos:vec = pos
        self.rect.topleft = pos
        self.angle = angle
        self.bullet_speed = bullet_speed
        self.collision_groups = game_controller.bullet_target_groups
        self.damage = damage
        self.hit_damage = kwargs.pop("hit_damage", damage)
        self.total_damage = damage
        self.owner_offset = vec(0,0)
        self.is_alive = True
        self.start_pos = pos
        self.start_time = datetime.datetime.now()
        self.hit_targets: list[int] = []
        self.rotation_angle = 0
        
        self.thrown = False
        self.was_grounded = False
        
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        
        self.hit_callback: function = kwargs.pop("hit_callback", lambda s: None)
        self.kill_callback: function = kwargs.pop("kill_callback", lambda s: None)
        
        self.max_range = kwargs.pop("max_range", 0)
        
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 0)
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 0)
        
        self.explosion_frame = 0
        self.exploding = False
        if self.explosion_max_radius > 0:
            self.explosion_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\explosion_01', convert_type=enums.ConvertType.CONVERT_ALPHA)
            self.explosion_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.HIT) + f'0{i}.mp3') for i in range(1,4)]
            for s in self.explosion_sounds:
                s.set_volume(0.1)
            
    def explosion_sound(self):
        sound = self.explosion_sounds[random.randint(0, len(self.explosion_sounds)-1)]

        sound.play()
        
    def update(self, **kwargs):
        if not self.is_alive:
            return
        
        self.acceleration.x = 0
        
        self.rotation_angle -= self.rotation_speed * self.speed.x
        if self.rotation_angle > 360:
            self.rotation_angle -= 360
        
        game = kwargs.pop("game", None)
        self.last_rect = self.rect.copy()
        
        if self.exploding:
            self.explosion_anim(0.5)
            return
        
        if self.max_range > 0:
            _distance = vec(self.rect.topleft).distance_to(vec(self.start_pos))
            if _distance >= self.max_range:
                self.destroy()
                
        if datetime.datetime.now() > self.start_time + datetime.timedelta(milliseconds=self.fuse_timeout_ms):
            self.destroy()
            
        # movement
        _new_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), self.bullet_speed, -math.radians(self.angle))
        if not self.thrown:
            _vector = vec(self.rect.topleft) - _new_pos
            self.speed -= _vector
            
        _ground_friction_multiplier = 8 if self.was_grounded else 1
        self.acceleration.x = round(self.acceleration.x + self.speed.x * (game.friction*self.friction_multiplier*_ground_friction_multiplier), 6)
        self.speed.x += round(self.acceleration.x, 6) * mc.dt
        self.pos.x += (self.speed.x + 0.5 * self.acceleration.x) * mc.dt
        
        # Gravity
        if self.is_alive and not self.exploding:
            self.last_rect = self.rect.copy()
            
            self.acceleration.y = game.gravity_accelaration
            self.speed.y += self.acceleration.y * mc.dt * self.gravity_scale
            self.pos.y += (self.speed.y + 0.5 * self.acceleration.y) * mc.dt
        
        self.rect.topleft = self.pos
        
        
        collided = self.bullet_collision()
        _last_y_speed = self.speed.y
        _ground_collided = self.ground_collision(game, game.collision_group)
        self.was_grounded = _ground_collided
        
        if _ground_collided and not self.detonate_on_impact:
            self.speed.y = -_last_y_speed * self.bounciness_multiplier
        
        if collided or _ground_collided:
            self.hit_callback(self)
            if self.detonate_on_impact:
                self.destroy()
                
        # if will be out of the map bounds
        _margin = 20
        if self.rect.centerx > game_controller.map_size.x + _margin or self.rect.centerx < -_margin or\
            self.rect.centery > game_controller.map_size.y + _margin or self.rect.centery < -_margin:
            self.kill()
        self.thrown = True
        
        
    def draw(self, screen: pygame.Surface, offset: vec):
        if not self.is_alive:
            return    
        
        if self.exploding:
            self.image = self.current_frame.copy()
        
        _image = self.image.copy()
            
        if self.rotation_speed != 0:
            _image = game_controller.rotate_image(self.image, self.rotation_angle)
        
        screen.blit(_image, vec(self.rect.topleft) - offset)
        
        # pygame.draw.circle(screen, colors.RED, self.rect.center - offset, self.explosion_min_radius, 2)
        
        # pygame.draw.rect(screen, colors.GREEN, ((self.rect.topleft) - offset, self.rect.size), 2)
    
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
            
            self.explosion_sound()
            self.exploding = True
        else:
            self.kill()
    
    def kill(self):
        self.is_alive = False
        self.kill_callback(len(self.hit_targets) > 0)
        super().kill()
    
    def bullet_collision(self):
        for group in self.collision_groups:
            collisions = pygame.sprite.spritecollide(self, group, False)
            for c in collisions:
                if c.id in self.hit_targets:
                    continue
                self.hit_targets.append(c.id)
                if (isinstance(c, Enemy) or isinstance(c, Rectangle)) and self.hit_damage > 0:
                    c.take_damage(self.hit_damage, self.owner)
                return True
        return False
    
    def ground_collision(self, game, targets: pygame.sprite.Group, obj = None):
        if obj == None:
            obj = self
        collision_objs = pygame.sprite.spritecollide(obj, targets, False)
        if collision_objs:
            game.collision(self, collision_objs, enums.Orientation.VERTICAL)
            return True
        return False  
    
    def get_netdata(self):
        values = {
            "id": self.id,
            "owner": self.owner,
            "angle": self.angle,
            "rect": tuple([*self.rect.topleft, *self.rect.size]),
            "speed": self.bullet_speed,
            "damage": self.damage,
            "bullet_type": str(self.bullet_type.name),
        }
        return values
    
    def load_netdata(self, data: dict):
        self.rect = pygame.Rect(data.pop("rect", (0,0, 1,1)))
        self.bullet_type = enums.BulletType[data.pop('bullet_type', enums.BulletType.PISTOL)]
        
        for item, value in data.items():
            setattr(self, item, value)