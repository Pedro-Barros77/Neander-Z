import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants, enums
from domain.content.weapons.projectile import Projectile
from domain.services import game_controller, menu_controller as mc, resources

class Launcher(Weapon):
    def __init__(self, pos, **kwargs):

        kwargs["bullet_type"] = enums.BulletType.ROCKET
        kwargs["weapon_type"] = enums.Weapons.RPG
        kwargs["is_primary"] = True
        super().__init__(pos, **kwargs)
        
        self.damage = 50
        self.bullet_speed = 15
        self.fire_rate = 1
        self.reload_delay_ms = 3000
        self.last_shot_time = None
        self.magazine_size = 1
        self.magazine_bullets = self.magazine_size
        self.bullet_max_range = 800
        self.bullet_min_range = 790
        self.explosion_min_radius = 100
        self.explosion_max_radius = 200
        self.fire_mode = enums.FireMode.SINGLE_SHOT
        self.reload_type = enums.ReloadType.SINGLE_BULLET
        
        self.barrel_offset = vec(0, 0)
        self.barrel_offset = vec(-15, 0)
        self.start_barrel_offset = self.barrel_offset.copy()
        
        self.bullet_spawn_offset = vec(self.rect.width/2 + 70,-10) + vec(self.barrel_offset)
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(enums.Weapons.RPG, enums.AnimActions.SHOOT), convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(resources.get_weapon_path(enums.Weapons.RPG, enums.AnimActions.RELOAD), convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The animation frames of this weapon when reloading."""
        self.reload_start_frame = 12
        self.playing_reload_start = False
        self.reload_end_frame = 17
        self.playing_reload_end = False
        
        self.idle_frame = self.fire_frames[0]
        self.idle_unloaded_frame = self.fire_frames[-1]
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.shoot_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.SHOOT))
        self.empty_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.EMPTY_TRIGGER))
        self.reload_start_sound_launcher = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.RELOAD))
        self.reload_end_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.RPG,enums.AnimActions.RELOAD_END))
   
        self.shoot_sound.set_volume(0.1)
        self.empty_sound.set_volume(0.1)
        self.reload_start_sound_launcher.set_volume(0.3)
        self.reload_end_sound.set_volume(0.5)
        
        
        self.current_bullet = None
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        if self.firing_frame < 1:
            self.firing_frame = 1
        
        if self.firing_frame > len(self.fire_frames)-1:
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
        self.current_bullet = Projectile(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, image_scale = 1.4, hit_callback = self.bullet_hit, explosion_max_radius = self.explosion_max_radius, explosion_min_radius = self.explosion_min_radius)
        return self.current_bullet
    
    def reload_anim(self, speed):
        self.reloading_frame += speed
        
        if int(self.reloading_frame) == self.reload_start_frame and not self.playing_reload_start:
            self.reload_start_sound_launcher.play()
            self.playing_reload_start = True
            
        if int(self.reloading_frame) == self.reload_end_frame and not self.playing_reload_end:
            self.reload_end_sound.play()
            self.playing_reload_end = True
            
        is_last_frame = self.reloading_frame > len(self.reload_frames)-1
        
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
            speed = ((10000/self.reload_delay_ms) / len(self.reload_frames)*2)
            self.reload_anim(speed * mc.dt)
            
    