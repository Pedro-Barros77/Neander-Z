import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants, enums
from domain.content.weapons.small_bullet import SmallBullet
from domain.services import game_controller, menu_controller as mc

class SMG(Weapon):
    def __init__(self, pos, **kwargs):
        
        kwargs["bullet_type"] = enums.BulletType.PISTOL
        kwargs["weapon_type"] = enums.Weapons.UZI
        kwargs["is_primary"] = True
        kwargs["weapon_distance"] = self.rect.width/2 + 30
        super().__init__(pos, **kwargs)
        
        self.damage = 4
        self.bullet_speed = 20
        self.fire_rate = 10
        self.reload_delay_ms = 1200
        self.magazine_size = 25
        self.magazine_bullets = self.magazine_size
        self.bullet_max_range = 600
        self.bullet_min_range = 400
        self.auto_fire = True
        
        self.bullet_spawn_offset = vec(self.rect.width/2 + 40, 2)
        self.last_shot_time = None
        
        self.fire_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.UZI, enums.AnimActions.SHOOT), 1.2, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.reload_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.UZI, enums.AnimActions.RELOAD), 1.2, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The animation frames of this weapon when reloading."""
        self.reload_end_frame = 11
        self.playing_reload_end = False
        
        self.idle_frame = game_controller.scale_image(pygame.image.load(constants.get_weapon_frames(enums.Weapons.UZI, enums.AnimActions.IDLE)), 1.2, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        self.barrel_offset = vec(0, 7)
        
        self.shoot_sounds = [pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.SHOOT, enums.SFXName.UZI_SHOOT).replace('.mp3', f'{i}.mp3')) for i in range(1,4)]
        self.empty_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.EMPTY_M, enums.SFXName.EMPTY_1911))
        self.reload_start_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.RELOAD, enums.SFXName.UZI_RELOAD))
        self.reload_end_sound = None
        
        self.last_channel = 0
   
        for s in self.shoot_sounds:
            s.set_volume(0.5)
            
   
        self.empty_sound.set_volume(0.1)
        self.reload_start_sound.set_volume(0.3)
        if self.reload_end_sound != None:
            self.reload_end_sound.set_volume(0.5)
            
    
    def fire_sound(self):
        sound = self.shoot_sounds[random.randint(0, len(self.shoot_sounds)-1)]
        
        
        pygame.mixer.Channel(self.last_channel).play(sound)
        self.last_channel += 1
        
        prev_chann = self.last_channel - 2
        if prev_chann >= 0:
            pygame.mixer.Channel(prev_chann).fadeout(200)
        
        if self.last_channel >= 4:
            self.last_channel = 0
            
        
    
    def fire_anim(self, speed: float):
        _still_firing = True
        self.firing_frame += speed
        
        if self.firing_frame > len(self.fire_frames)-1:
            self.firing_frame = 0
            _still_firing = False
            
            
        self.current_frame = self.fire_frames[int(self.firing_frame)]
        if not _still_firing:
            self.current_frame = self.idle_frame
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
        return _still_firing
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None
        
        super().shoot(bullet_pos, player_net_id, **kwargs)
        
        self.last_shot_time = datetime.datetime.now()
        
        self.fire_sound()
        return SmallBullet(bullet_pos, self.weapon_aim_angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id(), max_range = self.bullet_max_range, min_range = self.bullet_min_range)
    
    def reload_anim(self, speed):
        self.reloading_frame += speed
        
        if int(self.reloading_frame) == self.reload_end_frame and not self.playing_reload_end and self.reload_end_sound != None:
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
            self.firing = self.fire_anim(self.fire_rate/20 * mc.dt)
        if self.reloading:
            speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)*4)
            self.reload_anim(speed * mc.dt)
            