import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums
from domain.content.weapons.projectile import Projectile
from domain.services import game_controller, menu_controller as mc, resources

class Sniper(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.pierce_damage_multiplier = kwargs.pop("pierce_damage_multiplier", 1)
        self.max_pierce_targets = kwargs.pop("max_pierce_targets", 1)
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.RELOAD), self.weapon_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.pump_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.PUMP), self.weapon_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.playing_reload_end = False
        
        self.start_barrel_offset = self.barrel_offset.copy()
        
        self.shoot_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT))
        self.empty_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.EMPTY_TRIGGER))
        self.pump_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.PUMP))
        self.reload_start_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.reload_end_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD_END))
   
        self.pumping = False
        self.pumping_frame = 0
        
    def update(self, **kwargs):
        self.barrel_offset.x = self.start_barrel_offset.x * self.dir
        
        super().update(**kwargs)
        
        speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)* self.reload_speed_multiplier)
        
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
        
        return Projectile(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, pierce_damage_multiplier = self.pierce_damage_multiplier, max_pierce_targets = self.max_pierce_targets, kill_callback = self.bullet_kill_callback)
    

    
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

            
        
            
    