import pygame, math, datetime
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants, enums
from domain.content.weapons.small_bullet import SmallBullet
from domain.services import game_controller

class Pistol(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.bullet_type = enums.BulletType.PISTOL
        self.damage = 5
        self.bullet_speed = 30
        self.fire_rate = 5.5
        self.reload_delay_ms = 1000
        self.last_shot_time = None
        self.magazine_size = 7
        
        self.bullet_spawn_offset = vec(self.rect.width/2 + 5,0)
        # self.weapon_anchor = vec(self.rect.width/2, self.rect.height/3)
        
        
        self.fire_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.P_1911, enums.AnimActions.SHOOT))
        self.reload_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.P_1911, enums.AnimActions.RELOAD))
        """The animation frames of this weapon when reloading."""
        self.reload_end_frame = 6
        self.playing_reload_end = False
        
        self.idle_frame = self.fire_frames[0]
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        self.barrel_offset = vec(0, 7)
        
        self.shoot_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.SHOOT, enums.SFXName.P_1911))
        self.empty_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.EMPTY_M, enums.SFXName.EMPTY_1911))
        self.reload_start_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.RELOAD, enums.SFXName.START_RELOAD_1911))
        self.reload_end_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.RELOAD, enums.SFXName.END_RELOAD_1911))
   
        self.shoot_sound.set_volume(0.1)
        self.empty_sound.set_volume(0.1)
        self.reload_start_sound.set_volume(0.5)
        self.reload_end_sound.set_volume(0.5)
        
    
    def fire_anim(self):
        _still_firing = True
        self.firing_frame += self.fire_rate/20
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            _still_firing = False
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
        return _still_firing
    
    def shoot(self, bullet_pos: vec, player_net_id: int):
        if not self.can_shoot():
            return None
        
        super().shoot(bullet_pos, player_net_id)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sound.play()
        return SmallBullet(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id())
    
    def reload_anim(self, speed):
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

    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.firing:
            self.firing = self.fire_anim()
        if self.reloading:
            speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)*2)
            self.reload_anim(speed)
            
    