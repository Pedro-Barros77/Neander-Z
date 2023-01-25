import pygame, math, datetime,random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums
from domain.content.weapons.charge import Charge
from domain.services import game_controller, menu_controller as mc, resources

class Throwable(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        load_content = kwargs.pop("load_content", True)
        self.gravity_scale = kwargs.pop("gravity_scale", 1)
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 50)
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 100)
        self.fuse_timeout_ms = kwargs.pop("fuse_timeout_ms", 3000)
        self.detonate_on_impact = kwargs.pop("detonate_on_impact", True)
        self.bounciness_multiplier = kwargs.pop("bounciness_multiplier", 0.5)
        self.friction_multiplier = kwargs.pop("friction_multiplier", 0.2)
        self.hit_damage = kwargs.pop("hit_damage", self.damage)
        self.rotation_speed = kwargs.pop("rotation_speed", 5)
        self.throwing = False
        self.throwing_frame = 0
        self.throw_end_frame = 6
        self.throw_callback = lambda x: None
        
        self.cook_start_time = None
        
        self.charges = []
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.hit_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.HIT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.hand_frames = [game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}weapons\\throwables\\throwing_hand\\hand\\0{i}.png'), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA) for i in range(1,10)]
        self.fingers_frames = [game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}weapons\\throwables\\throwing_hand\\fingers\\0{i}.png'), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA) for i in range(1,10)]
        
        self.hand_surface: pygame.Surface = pygame.Surface(self.hand_frames[0].get_size(), pygame.SRCALPHA)
        
        self.shoot_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT) + f'0{i}.mp3') for i in range(1,3)]
        self.reload_start_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.hit_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.HIT))
    
    def update(self, **kwargs):
        super().update(**kwargs)
        
        speed = ((1000/self.reload_delay_ms) / len(self.hand_frames)* self.reload_speed_multiplier)
        if self.firing:
            self.fire_anim(self.fire_rate/20 * mc.dt)
        if self.reloading:
            self.load_anim(speed * mc.dt)
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
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            self.firing = False
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
            
    def throw_anim(self, speed: float):
        self.throwing_frame += speed
        
        # if int(self.throwing_frame) == self.throw_end_frame:
        #     self.throw_callback(self.charges)

        if self.throwing_frame > len(self.hand_frames):
            self.throwing_frame = 0
            self.throwing = False
            self.hand_surface.fill((0,0,0,0))
            return
        
        self.hand_surface.fill((0,0,0,0))
        self.hand_surface.blit(self.hand_frames[int(self.throwing_frame)], (0,0))
        self.hand_surface.blit(self.fingers_frames[int(self.throwing_frame)], (0,0))
             
    def cook_grenade(self):
        if self.throwing or self.cook_start_time != None:
            return
        self.cook_start_time = datetime.datetime.now()
        
        self.reload_start_sound.play()
        
        self.hand_surface.blit(self.hand_frames[0], (0,0))
        self.hand_surface.blit(self.current_frame, (0,0))
        self.hand_surface.blit(self.fingers_frames[0], (0,0))
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None

        self.throwing = True
        self.firing = True
        self.bullet_kill_callback = kwargs.pop("kill_callback", lambda b: None)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sounds[random.randint(0, len(self.shoot_sounds)-1)].play()
        self.cook_start_time = None
        
        charge_dict = {
            "max_range": self.bullet_max_range,
            "min_range": self.bullet_min_range,
            "bullet_type": self.bullet_type,
            "kill_callback": self.bullet_kill_callback,
            "gravity_scale": self.gravity_scale,
            "explosion_min_radius": self.explosion_min_radius,
            "explosion_max_radius": self.explosion_max_radius,
            "fuse_timeout_ms": self.fuse_timeout_ms,
            "detonate_on_impact": self.detonate_on_impact,
            "bounciness_multiplier": self.bounciness_multiplier,
            "friction_multiplier": self.friction_multiplier,
            "hit_damage": self.hit_damage,
            "rotation_speed": self.rotation_speed
        }
        
        return Charge(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), **charge_dict)
    
    def load_anim(self, speed):
        self.reloading_frame += speed
        
        if int(self.reloading_frame) == self.reload_end_frame and not self.playing_reload_end:
            self.reload_end_sound.play()
            self.playing_reload_end = True
            
        is_last_frame = self.reloading_frame > len(self.reload_frames)-1
        
        if is_last_frame:
            self.reloading_frame = 0
            self.reloading = False
            self.playing_reload_end = False
        self.current_frame = self.reload_frames[int(self.reloading_frame)]
        
        if is_last_frame:
            self.current_frame = self.idle_frame
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
            
    