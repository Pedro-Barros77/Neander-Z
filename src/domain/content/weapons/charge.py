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
        self.effect_timeout_ms = kwargs.pop("effect_timeout_ms", 3000)
        self.detonate_on_impact = kwargs.pop("detonate_on_impact", True)
        self.bounciness_multiplier = kwargs.pop("bounciness_multiplier", 0.5)
        self.friction_multiplier = kwargs.pop("friction_multiplier", 0.2)
        self.rotation_speed = kwargs.pop("rotation_speed", 5)
        self.image = game_controller.load_sprites(resources.get_weapon_path(self.charge_type, enums.AnimActions.SHOOT), self.image_scale, enums.ConvertType.CONVERT_ALPHA)[0]
        self.anim_frames = kwargs.pop("anim_frames", [self.image])
        self.current_frame: pygame.Surface = self.image.copy()
        self.rect = self.image.get_rect()
        self.last_rect = self.rect.copy()
        self.pos:vec = pos
        self.rect.topleft = pos
        self.angle = angle
        self.bullet_speed = bullet_speed
        self.solid_collision_groups = game_controller.collision_group
        self.target_collision_groups = game_controller.bullet_target_groups
        self.damage = damage
        self.hit_damage = kwargs.pop("hit_damage", damage)
        self.total_damage = damage
        self.owner_offset = vec(0,0)
        self.is_alive = True
        self.start_pos = pos
        self.start_time = kwargs.pop("start_time", datetime.datetime.now())
        self.destroy_time = kwargs.pop("destroy_time", None)
        self.hit_targets: list[int] = []
        self.rotation_angle = 0
        
        self.thrown = False
        self.was_grounded = False
        
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        
        self.charge_destroy_pos = vec(0,0)
        self.hit_callback: function = kwargs.pop("hit_callback", lambda s: None)
        self.kill_callback: function = kwargs.pop("kill_callback", lambda s: None)
        
        self.max_range = kwargs.pop("max_range", 0)
        
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 0)
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 0)
        
        self.last_hit_sound = datetime.datetime.now() - datetime.timedelta(milliseconds=2000)
        self.hit_interval_ms = 100
        
        self.idle_frame = 0
        self.animating_idle = True
        self.idle_anim_speed = kwargs.pop("anim_speed", 1)
        
        self.explosion_frame = 0
        self.exploding = False
        if self.explosion_max_radius > 0:
            self.explosion_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\explosion_01', convert_type=enums.ConvertType.CONVERT_ALPHA)
            self.explosion_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.HIT) + f'0{i}.mp3') for i in range(1,4)]
            for s in self.explosion_sounds:
                s.set_volume(0.1)
                
                
        self.floor_fire_frames_start, self.floor_fire_frames_end, self.floor_fire_frames_loop, self.floor_fire_surface = None, None, None, None
        self.burn_frame = 0
        self.burning_loop = False
        self.burning_start = False
        self.burning_end = False
        self.burn_tick_ms = kwargs.pop("burn_tick_ms", 500)
        self.last_burn_tick = datetime.datetime.now()
        self.burn_hitbox: Rectangle = None
        if self.charge_type == enums.Throwables.MOLOTOV:
            self.floor_fire_frames_start = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\floor_flames\\start',2, enums.ConvertType.CONVERT_ALPHA)
            self.floor_fire_frames_end = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\floor_flames\\end',2, enums.ConvertType.CONVERT_ALPHA)
            self.floor_fire_frames_loop = game_controller.load_sprites(f'{resources.IMAGES_PATH}weapons\\effects\\floor_flames\\loop',2, enums.ConvertType.CONVERT_ALPHA)
            self.floor_fire_surface = self.floor_fire_frames_start[0].copy()
                
        
            
    def explosion_sound(self):
        sound = self.explosion_sounds[random.randint(0, len(self.explosion_sounds)-1)]

        sound.play()
        
    def update(self, **kwargs):
        if not self.is_alive:
            return
        
        _now = datetime.datetime.now()
        
        self.acceleration.x = 0
        
        if not self.exploding:
            self.rotation_angle -= self.rotation_speed * self.speed.x
            if self.rotation_angle > 360:
                self.rotation_angle -= 360
        
        game = kwargs.pop("game", None)
        self.last_rect = self.rect.copy()
        
        if self.exploding:
            self.explosion_anim(0.5)
            return
        
        _burn_speed = 0.15
        if self.burning_start:
            self.burn_start_anim(_burn_speed * 1.5 * mc.dt)
            
        if self.burning_loop:
            self.burn_loop_anim(_burn_speed * mc.dt)
            
        if self.burning_end:
            self.burn_end_anim(_burn_speed * mc.dt)
            
        if self.burning_start or self.burning_loop:
            if _now > self.last_burn_tick + datetime.timedelta(milliseconds=self.burn_tick_ms):
                if self.destroy_time == None or _now < self.destroy_time + datetime.timedelta(milliseconds=self.effect_timeout_ms):
                    self.last_burn_tick = _now
                    self.fire_damage()
                else:
                    self.burning_loop = False
                    self.burning_end = True
            return
        
        if self.burning_end:
            return

        if self.animating_idle:
            self.idle_anim(self.idle_anim_speed)
        
        if self.max_range > 0:
            _distance = vec(self.rect.topleft).distance_to(vec(self.start_pos))
            if _distance >= self.max_range:
                self.destroy()
                
        if self.fuse_timeout_ms > 0 and datetime.datetime.now() > self.start_time + datetime.timedelta(milliseconds=self.fuse_timeout_ms):
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
        
        
        collided = self.bullet_collision([self.solid_collision_groups])
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
        
        if self.floor_fire_surface != None and (self.burning_start or self.burning_loop or self.burning_end) and self.burn_hitbox != None:
            screen.blit(self.floor_fire_surface, maths.rect_offset(self.burn_hitbox.rect, - offset))
            return
            
            
        self.image = self.current_frame.copy()
        
        _image = self.image.copy()
            
        if self.rotation_speed != 0 and not self.exploding:
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
            
    def idle_anim(self, speed: float):
        self.idle_frame += speed
        
        if self.idle_frame > len(self.anim_frames):
            self.idle_frame = 0
        else:
            self.current_frame = self.anim_frames[int(self.idle_frame)]
            
    def burn_start_anim(self, speed: float):
        self.burn_frame += speed
        
        if self.burn_frame > len(self.floor_fire_frames_start):
            self.burn_frame = 0
            self.burning_start = False
            self.burning_loop = True
        self.floor_fire_surface = self.floor_fire_frames_start[int(self.burn_frame)]
    
    def burn_loop_anim(self, speed: float):
        self.burn_frame += speed
        
        if self.burn_frame > len(self.floor_fire_frames_loop):
            self.burn_frame = 0
        self.floor_fire_surface = self.floor_fire_frames_loop[int(self.burn_frame)]
        
    def burn_end_anim(self, speed: float):
        self.burn_frame += speed
        
        if self.burn_frame > len(self.floor_fire_frames_end)-1:
            self.burn_frame = 0
            self.burning_start = False
            self.burning_end = False
            self.burning_loop = False
            self.kill()
            
        self.floor_fire_surface = self.floor_fire_frames_end[int(self.burn_frame)]
            
    def fire_damage(self):
        groups = self.target_collision_groups + game_controller.enemy_target_groups
        for group in groups:
            collided_fire = pygame.sprite.spritecollide(self.burn_hitbox, group, False)
            for c in collided_fire:
                if (not isinstance(c, Enemy) and not isinstance(c, Rectangle)) and (c.name != "zombie_body" and c.name != "player_body"):
                    continue
                
                c.take_damage(self.damage, self.owner)
    
    def destroy(self):
        self.destroy_time = datetime.datetime.now()
        self.kill_callback(self)
    
    def kill(self):
        self.is_alive = False
        super().kill()
    
    def bullet_collision(self, groups: list[pygame.sprite.Group]):
        for group in groups:
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