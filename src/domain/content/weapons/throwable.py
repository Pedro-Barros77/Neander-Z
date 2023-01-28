import pygame, math, datetime,random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums
from domain.content.weapons.charge import Charge
from domain.models.rectangle_sprite import Rectangle
from domain.models.enemy import Enemy
from domain.services import game_controller, menu_controller as mc, resources

class Throwable(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        load_content = kwargs.pop("load_content", True)
        self.gravity_scale = kwargs.pop("gravity_scale", 1)
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 50)
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 100)
        self.fuse_timeout_ms = kwargs.pop("fuse_timeout_ms", 3000)
        self.effect_timeout_ms = kwargs.pop("effect_timeout_ms", 3000)
        self.detonate_on_impact = kwargs.pop("detonate_on_impact", True)
        self.bounciness_multiplier = kwargs.pop("bounciness_multiplier", 0.5)
        self.friction_multiplier = kwargs.pop("friction_multiplier", 0.2)
        self.hit_damage = kwargs.pop("hit_damage", self.damage)
        self.rotation_speed = kwargs.pop("rotation_speed", 5)
        self.charge_offset = kwargs.pop("charge_offset", vec(0,0))
        self.anim_speed = kwargs.pop("anim_speed", 1)
        self.throwing = False
        self.throwing_frame = 0
        self.throw_end_frame = 6
        self.throw_callback = lambda x: None
        self.count = kwargs.pop("count", 1)
        
        self.cook_frame = 0
        
        self.cook_start_time = None
        
        self.charges = []
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.hit_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.HIT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.hand_frames = [game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}weapons\\throwables\\throwing_hand\\hand\\0{i}.png'), 0.8, enums.ConvertType.CONVERT_ALPHA) for i in range(1,10)]
        self.fingers_frames = [game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}weapons\\throwables\\throwing_hand\\fingers\\0{i}.png'), 0.8, enums.ConvertType.CONVERT_ALPHA) for i in range(1,10)]
        
        self.hand_surface: pygame.Surface = pygame.Surface( self.hand_frames[0].get_size(), pygame.SRCALPHA)
        
        self.shoot_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT) + f'0{i}.mp3') for i in range(1,3)]
        self.reload_start_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.hit_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.HIT) + f'0{i}.mp3') for i in range(1,3)]

    def update(self, **kwargs):
        super().update(**kwargs)
        
        speed = ((1000/self.reload_delay_ms) / len(self.hand_frames)* self.reload_speed_multiplier)
        if self.cook_start_time != None:
            self.cook_anim(self.anim_speed * mc.dt)
        if self.throwing:
            self.throw_anim(speed * mc.dt)
            
        
            
    def draw(self, screen: pygame.Surface, offset: vec):
        
        hand_surface = self.hand_surface.copy()
        if self.dir < 0:
            hand_surface = pygame.transform.flip(hand_surface, False, True)
        hand_pos = game_controller.point_to_angle_distance(vec(self.rect.topleft), -self.weapon_distance*1.4, -math.radians(self.weapon_aim_angle))
        hand_pos.y -= 30
        hand_sur, hand_rect = game_controller.rotate_to_angle(hand_surface, hand_pos, self.weapon_aim_angle)
        
        screen.blit(hand_sur, hand_rect)
        
        
    def cook_anim(self, speed: float):
        self.cook_frame += speed
        
        if self.cook_frame > len(self.fire_frames):
            self.cook_frame = 0
        self.current_frame = self.fire_frames[int(self.cook_frame)]
        self.draw_hand()
            
    def throw_anim(self, speed: float):
        self.throwing_frame += speed
        
        if self.throwing_frame > len(self.hand_frames):
            self.throwing_frame = 0
            self.throwing = False
            self.hand_surface.fill((0,0,0,0))
            return
        
        self.hand_surface.fill((0,0,0,0))
        self.hand_surface.blit(self.hand_frames[int(self.throwing_frame)], (0,0))
        self.hand_surface.blit(self.fingers_frames[int(self.throwing_frame)], (0,0))
        
    def can_shoot(self):
        # if ran out of ammo
        if self.count <= 0:
            return False
        
        _now = datetime.datetime.now()
        
        #if the player is switching weapons
        if self.changing_weapon:
            return False
        
        # if is still reloading
        if self.reload_start_time != None and _now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time:
            return False
        
        if self.last_shot_time != None and _now - datetime.timedelta(milliseconds= self.fire_rate_ratio/self.fire_rate) > self.last_shot_time:
            return True
        
        return False
    
    def draw_hand(self, draw_charge = True):
        self.hand_surface.fill((0,0,0,0))
        self.hand_surface.blit(self.hand_frames[0], (0,0))
        if draw_charge:
            self.hand_surface.blit(self.current_frame, vec(30 - self.current_frame.get_width()/2, self.hand_surface.get_height()/2 - self.current_frame.get_height()/2) + self.charge_offset)
        self.hand_surface.blit(self.fingers_frames[0], (0,0))
             
    def cook_grenade(self):
        if not self.can_shoot() and self.last_shot_time != None:
            return None
        
        if self.throwing or self.cook_start_time != None or self.count == 0:
            return
        
        self.cook_start_time = datetime.datetime.now()
        
        self.reload_start_sound.play()
        
        self.draw_hand()
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot() and self.last_shot_time != None:
            return None

        self.count -= 1
        self.throwing = True
        self.firing = True
        self.bullet_kill_callback = kwargs.pop("kill_callback", lambda b: None)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sounds[random.randint(0, len(self.shoot_sounds)-1)].play()
        
        charge_dict = {
            "charge_type": self.weapon_type,
            "max_range": self.bullet_max_range,
            "min_range": self.bullet_min_range,
            "bullet_type": self.bullet_type,
            "gravity_scale": self.gravity_scale,
            "explosion_min_radius": self.explosion_min_radius,
            "explosion_max_radius": self.explosion_max_radius,
            "fuse_timeout_ms": self.fuse_timeout_ms,
            "effect_timeout_ms": self.effect_timeout_ms,
            "detonate_on_impact": self.detonate_on_impact,
            "bounciness_multiplier": self.bounciness_multiplier,
            "friction_multiplier": self.friction_multiplier,
            "hit_damage": self.hit_damage,
            "rotation_speed": self.rotation_speed,
            "start_time": self.cook_start_time,
            "image_scale": self.weapon_scale,
            "anim_frames": self.fire_frames,
            "anim_speed": self.anim_speed,
            "kill_callback": self.on_charge_destroy,
            "hit_callback": self.on_charge_hit
        }
        self.cook_start_time = None
        
        return Charge(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), **charge_dict)
            
            
    def on_charge_hit(self, charge: Charge):
        _now = datetime.datetime.now()
        match self.weapon_type:
            case enums.Throwables.FRAG_GRENADE:
                if charge.last_hit_sound != None and _now > charge.last_hit_sound + datetime.timedelta(milliseconds=charge.hit_interval_ms):
                    self.hit_sounds[random.randint(0, len(self.hit_sounds)-1)].play()
                    charge.last_hit_sound = _now
                else:
                    charge.last_hit_sound = None
            
    def on_charge_destroy(self, charge: Charge):
        match self.weapon_type:
            case enums.Throwables.FRAG_GRENADE:
                self.explode_charge(charge)
            case enums.Throwables.MOLOTOV:
                self.spawn_floor_flames(charge)
                
        self.bullet_kill_callback(len(charge.hit_targets) > 0)
    
    
    def explode_charge(self, charge: Charge):
        if charge.explosion_min_radius == 0:
            charge.kill()
            return
        
        for group in charge.target_collision_groups + game_controller.enemy_target_groups:
            _explosion_min_hitbox = Rectangle((charge.explosion_min_radius*2, charge.explosion_min_radius*2), vec(charge.rect.topleft), radius = charge.explosion_min_radius)
            _explosion_min_hitbox.rect.center = charge.rect.center
            _explosion_max_hitbox = Rectangle((charge.explosion_max_radius*2, charge.explosion_max_radius*2), vec(charge.rect.topleft), radius = charge.explosion_max_radius)
            _explosion_max_hitbox.rect.center = charge.rect.center
            
            collided_explosion = pygame.sprite.spritecollide(_explosion_max_hitbox, group, False, pygame.sprite.collide_circle)
            for c in collided_explosion:
                if (not isinstance(c, Enemy) and not isinstance(c, Rectangle)) and (c.name != "zombie_body" and c.name != "player_body"):
                    continue
                    
                _distance = vec(charge.rect.center).distance_to(c.rect.center)
                if _distance >= charge.explosion_max_radius:
                    break
                if _distance > charge.explosion_min_radius:
                    _diff = _distance - charge.explosion_min_radius
                    _range = charge.explosion_max_radius - charge.explosion_min_radius
                    
                    _percentage = (_diff * 100 / _range) / 100
                    
                    charge.damage = charge.total_damage - (_percentage * charge.total_damage)
                
                c.take_damage(charge.damage, charge.owner)
        
        charge.explosion_sound()
        charge.exploding = True
        
        
    def spawn_floor_flames(self, charge: Charge):
        self.hit_sounds[random.randint(0, len(self.hit_sounds)-1)].play()
        charge.charge_destroy_pos = vec(charge.rect.bottomleft)
        charge.burning_start = True
        charge.animating_idle = False
        
        _fire_rect = charge.floor_fire_surface.get_rect()
        _fire_rect.centerx = charge.charge_destroy_pos.x
        _fire_rect.bottom = charge.charge_destroy_pos.y
        charge.burn_hitbox = Rectangle(_fire_rect.size, _fire_rect.topleft)
        # charge.kill()
    
    
        