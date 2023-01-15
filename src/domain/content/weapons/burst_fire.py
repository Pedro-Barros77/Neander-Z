import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums
from domain.content.weapons.projectile import Projectile
from domain.services import game_controller, menu_controller as mc, resources

class BurstFire(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.burst_fire_rate = kwargs.pop("burst_fire_rate", 10)
        self.burst_count = kwargs.pop("burst_count", 3)
        self.current_burst_round = 0
        self.last_burst_time = datetime.datetime.now()
        self.firing_burst = False
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.fire_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.RELOAD), self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        """The animation frames of this weapon when reloading."""
        
        self.reload_start_frame = kwargs.pop("reload_start_frame", 0)
        self.playing_reload_start = False
        self.playing_reload_end = False
        
        self.shoot_sounds =[pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT) + f'0{i}.mp3') for i in range(1,3)]
        self.empty_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.EMPTY_TRIGGER))
        self.reload_start_sound_burst = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD))
        self.reload_end_sound = pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.RELOAD_END))
        self.last_channel = 0
        
    def fire_sound(self):
        sound = self.shoot_sounds[random.randint(0, len(self.shoot_sounds)-1)]
        pygame.mixer.Channel(self.last_channel).play(sound)
        self.last_channel += 1
        
        prev_chann = self.last_channel - 2
        if prev_chann >= 0:
            pygame.mixer.Channel(prev_chann).fadeout(200)
        
        if self.last_channel >= 4:
            self.last_channel = 0
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.firing:
            self.fire_anim(self.burst_fire_rate/20 * mc.dt)
        if self.reloading:
            speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)*self.reload_speed_multiplier)
            self.reload_anim(speed * mc.dt)
    
    def reload(self):
        super().reload()
        self.current_burst_round = 0
        
    def shoot_one(self, bullet_pos: vec, player_net_id: int, **kwargs):
        _now = datetime.datetime.now()
        
        if self.last_shot_time != None and _now - datetime.timedelta(milliseconds= self.fire_rate_ratio/self.burst_fire_rate) < self.last_shot_time:
            return None
        
        if self.magazine_bullets <= 0:
            return None
        
        self.firing_burst = True
        super().shoot(bullet_pos, player_net_id, **kwargs)
        
        self.current_burst_round += 1
        
        self.last_shot_time = _now
        self.fire_sound()
        return Projectile(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range, bullet_type = self.bullet_type, kill_callback = self.bullet_kill_callback)
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None
        
        projectile = self.shoot_one(bullet_pos, player_net_id, **kwargs)
        
        if self.current_burst_round >= self.burst_count:
            self.current_burst_round = 0
            self.last_burst_time = datetime.datetime.now()
            self.firing_burst = False
            
        return projectile

        
    
    def can_shoot(self):
        # if ran out of ammo
        if self.magazine_bullets <= 0:
            self.firing_burst = False
            if "mouse_0" in mc.pages_history[-1].pressed_keys:
                mc.pages_history[-1].pressed_keys.remove("mouse_0")
            if self.empty_sound != None:
                self.empty_sound.play()
            return False
        
        _now = datetime.datetime.now()
        
        #if the player is switching weapons
        if self.changing_weapon:
            return False
        
        # if is still reloading
        if self.reload_start_time != None and _now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time:
            return False
        
        if self.last_shot_time == None:
            return True
        
        if _now - datetime.timedelta(milliseconds= self.fire_rate_ratio/self.fire_rate) > self.last_burst_time:
            return True
        
        return False
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            self.firing = False
                
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
    
    def reload_anim(self, speed):
        self.reloading_frame += speed
        
        if int(self.reloading_frame) == self.reload_start_frame and not self.playing_reload_start:
            self.reload_start_sound_burst.play()
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
