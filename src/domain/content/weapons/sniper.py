import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants, enums
from domain.content.weapons.projectile import Projectile
from domain.services import game_controller, menu_controller as mc, resources

class Sniper(Weapon):
    def __init__(self, pos, **kwargs):
        
        kwargs["bullet_type"] = enums.BulletType.SNIPER
        kwargs["weapon_type"] = enums.Weapons.SV98
        kwargs["is_primary"] = True
        super().__init__(pos, **kwargs)
        
        self.damage = 30
        self.bullet_speed = 35
        self.fire_rate = 1
        self.reload_delay_ms = 1500
        self.last_shot_time = None
        self.magazine_size = 10
        self.magazine_bullets = self.magazine_size
        self.bullet_max_range = 1200
        self.bullet_min_range = 1000
        self.fire_mode = enums.FireMode.BOLT_ACTION
        self.reload_type = enums.ReloadType.MAGAZINE
        self.pierce_damage_multiplier = 0.5
        self.max_pierce_targets = 5
        self.weapon_switch_ms = 400
        
        self.bullet_spawn_offset = vec(self.rect.width/2 + 45, -3)
        
        _scale = 1.1
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(enums.Weapons.SV98, enums.AnimActions.SHOOT), _scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(resources.get_weapon_path(enums.Weapons.SV98, enums.AnimActions.RELOAD), _scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.pump_frames = game_controller.load_sprites(resources.get_weapon_path(enums.Weapons.SV98, enums.AnimActions.PUMP), _scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.reload_end_frame = 17
        self.playing_reload_end = False
        
        self.idle_frame = self.fire_frames[0]
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        self.barrel_offset = vec(10, -5)
        self.start_barrel_offset = self.barrel_offset.copy()
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.shoot_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.SV98,enums.AnimActions.SHOOT))
        self.empty_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.SV98,enums.AnimActions.EMPTY_TRIGGER))
        self.pump_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.SV98,enums.AnimActions.PUMP))
        self.reload_start_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.SV98,enums.AnimActions.RELOAD))
        self.reload_end_sound = pygame.mixer.Sound(resources.get_weapon_sfx(enums.Weapons.SV98,enums.AnimActions.RELOAD_END))
   
        self.shoot_sound.set_volume(0.5)
        self.pump_sound.set_volume(0.5)
        self.empty_sound.set_volume(0.1)
        self.reload_start_sound.set_volume(0.3)
        self.reload_end_sound.set_volume(0.3)
        
        self.pumping = False
        self.pumping_frame = 0
        
    def update(self, **kwargs):
        self.barrel_offset.x = self.start_barrel_offset.x * self.dir
        
        super().update(**kwargs)
        
        speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)*9)
        
        if self.firing:
            self.firing = self.fire_anim(self.fire_rate/5 * mc.dt)
        if self.reloading and not self.pumping:
            self.reload_anim(speed * mc.dt)
        if self.pumping:
            self.pump_anim(speed * mc.dt)
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot() or self.pumping or self.reloading:
            return None
        
        super().shoot(bullet_pos, player_net_id, **kwargs)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sound.play()
        
        return Projectile(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, pierce_damage_multiplier = self.pierce_damage_multiplier, max_pierce_targets = self.max_pierce_targets)
    

    
    # def reload(self):
    #     now = datetime.datetime.now()
    #     # if ran out of ammo
    #     if self.player_backpack.get_ammo(self.bullet_type) <= 0:
    #         return False
    #     # if magazine is full
    #     if self.magazine_bullets >= self.magazine_size:
    #         return False
    #     # if is still reloading
    #     if (self.reload_start_time != None and now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time) or self.pumping:
    #         return False
    #     # if is still firing
    #     if self.firing:
    #         return False
        
        
    #     self.reloading = True
    #     self.reload_start_time = now
        
    # def reload_one(self):
    #     now = datetime.datetime.now()
        
    #     # if ran out of ammo
    #     if self.player_backpack.get_ammo(self.bullet_type) <= 0:
    #         return False
    #     # if magazine is full
    #     if self.magazine_bullets >= self.magazine_size:
    #         return False
    #     # if is still reloading
    #     if (self.reload_start_time != None and now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time) or self.pumping:
    #         return False
    #     # if is still firing
    #     if self.firing:
    #         return False
        
    #     self.magazine_bullets += 1
    #     self.player_backpack.set_ammo(self.player_backpack.get_ammo(self.bullet_type)-1, self.bullet_type)
            
    #     _will_fit_one_more = self.magazine_bullets +1 <= self.magazine_size and self.player_backpack.get_ammo(self.bullet_type) > 0
    #     if not _will_fit_one_more:
    #         self.pumping = True
    #     return _will_fit_one_more

    def fire_anim(self, speed: float):
        _still_firing = True
        self.firing_frame += speed
        
        if self.firing_frame > len(self.fire_frames):
            self.firing_frame = 0
            _still_firing = False
            self.pumping = True
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
        return _still_firing
    
    def pump_anim(self, speed):
        if self.pumping_frame == 0:
            self.pump_sound.play()
        self.pumping_frame += speed
        
        if self.pumping_frame > len(self.pump_frames):
            self.pumping_frame = 0
            self.pumping = False
            self.current_frame = self.idle_frame
        else:
            self.current_frame = self.pump_frames[int(self.pumping_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
    
    
    def reload_anim(self, speed):
        self.reloading_frame += speed
        if self.reloading_frame == 0:
            self.reload_start_time = datetime.datetime.now()
        
        if int(self.reloading_frame) == self.reload_end_frame and not self.playing_reload_end:
            self.reload_end_sound.play()
            self.playing_reload_end = True
            
        
        if self.reloading_frame > len(self.reload_frames):
            # self.reloading = self.reload_one()
            self.pumping = True
            self.reloading = False
            
            self.reloading_frame = 0
            self.playing_reload_end = False
            self.current_frame = self.idle_frame
        else:
            self.current_frame = self.reload_frames[int(self.reloading_frame)]
            
        
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)

            
        
            
    