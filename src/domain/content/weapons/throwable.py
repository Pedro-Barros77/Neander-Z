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
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.hit_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.HIT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        
        self.shoot_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT) + f'0{i}.mp3') for i in range(1,3)]
        self.reload_start_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.hit_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.HIT))
    
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.firing:
            self.fire_anim(self.fire_rate/20 * mc.dt)
        if self.reloading:
            speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)* self.reload_speed_multiplier)
            self.load_anim(speed * mc.dt)
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None

        self.firing = True
        self.bullet_kill_callback = kwargs.pop("kill_callback", lambda b: None)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sounds[random.randint(0, len(self.shoot_sounds)-1)].play()
        return Charge(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, kill_callback = self.bullet_kill_callback, gravity_scale = self.gravity_scale, explosion_min_radius = self.explosion_min_radius, explosion_max_radius = self.explosion_max_radius, fuse_timeout_ms = self.fuse_timeout_ms, detonate_on_impact = self.detonate_on_impact, bounciness_multiplier = self.bounciness_multiplier, friction_multiplier = self.friction_multiplier, hit_damage = self.hit_damage)
    
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
            
    