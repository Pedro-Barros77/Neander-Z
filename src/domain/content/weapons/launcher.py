import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums
from domain.content.weapons.projectile import Projectile
from domain.services import game_controller, menu_controller as mc, resources

class Launcher(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.explosion_min_radius = kwargs.pop("explosion_min_radius", 50)
        self.explosion_max_radius = kwargs.pop("explosion_max_radius", 100)
        
        self.start_barrel_offset = self.barrel_offset.copy()
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.RELOAD), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        """The animation frames of this weapon when reloading."""
        
        self.reload_start_frame = kwargs.pop("reload_start_frame", 0)
        self.playing_reload_start = False
        self.playing_reload_end = False
        
        self.idle_unloaded_frame = self.fire_frames[-1]
        
        self.shoot_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT))
        self.empty_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.EMPTY_TRIGGER))
        self.reload_start_sound_launcher = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.reload_end_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD_END))
   
        self.current_bullet = None
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        if self.firing_frame < 1:
            self.firing_frame = 1
        
        if self.firing_frame > len(self.fire_frames):
            self.firing_frame = 0
            self.firing = False
            self.current_frame = self.idle_unloaded_frame
        else:
            self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
            
    def bullet_hit(self, b):
        self.shoot_sound.fadeout(500)
        
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None
        
        super().shoot(bullet_pos, player_net_id, **kwargs)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sound.play()
        self.current_bullet = Projectile(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, image_scale = 1.4, hit_callback = self.bullet_hit, explosion_max_radius = self.explosion_max_radius, explosion_min_radius = self.explosion_min_radius, kill_callback = self.bullet_kill_callback)
        return self.current_bullet
    
    def reload_anim(self, speed):
        self.reloading_frame += speed
        
        if int(self.reloading_frame) == self.reload_start_frame and not self.playing_reload_start:
            self.reload_start_sound_launcher.play()
            self.playing_reload_start = True
            
        if int(self.reloading_frame) == self.reload_end_frame and not self.playing_reload_end:
            self.reload_end_sound.play()
            self.playing_reload_end = True
            
        is_last_frame = self.reloading_frame > len(self.reload_frames)
        
        if is_last_frame:
            self.reloading_frame = 0
            self.reloading = False
            self.playing_reload_end = False
            self.playing_reload_start = False
        self.current_frame = self.reload_frames[int(self.reloading_frame)]
        
        if is_last_frame:
            self.current_frame = self.idle_frame
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)

    def update(self, **kwargs):
        self.barrel_offset.x = self.start_barrel_offset.x * self.dir
        
        if self.weapon_aim_angle > 45 and self.weapon_aim_angle < 90:
            self.barrel_offset.x += (self.weapon_aim_angle - (90 - self.weapon_aim_angle))/4.5
        elif self.weapon_aim_angle > 90 and self.weapon_aim_angle < 135:
            self.barrel_offset.x += (self.weapon_aim_angle - (135 - self.weapon_aim_angle))/4.5 - 30
        elif self.weapon_aim_angle < -90 and self.weapon_aim_angle > -135:
            self.barrel_offset.x -= (self.weapon_aim_angle + (135 + self.weapon_aim_angle))/4.5 + 30
        elif self.weapon_aim_angle < -45 and self.weapon_aim_angle > -90:
            self.barrel_offset.x -= (self.weapon_aim_angle + (90 + self.weapon_aim_angle))/4.5
            
        super().update(**kwargs)
        
        if self.firing:
            self.fire_anim(self.fire_rate/5 * mc.dt)
        if self.reloading:
            speed = ((10000/self.reload_delay_ms) / len(self.reload_frames)* self.reload_speed_multiplier)
            self.reload_anim(speed * mc.dt)
            
    