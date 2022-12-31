import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants, enums
from domain.content.weapons.small_bullet import SmallBullet
from domain.services import game_controller

class Shotgun(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.bullet_type = enums.BulletType.SHOTGUN
        self.damage = 3
        self.bullet_speed = 20
        self.fire_rate = 1.5
        self.reload_delay_ms = 500
        self.last_shot_time = None
        self.magazine_size = 5
        self.magazine_bullets = self.magazine_size
        self.dispersion = 50
        
        self.bullet_spawn_offset = vec(self.rect.width/2 + 45, 5)
        
        _scale = 1.5
        self.fire_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.SHORT_BARREL, enums.AnimActions.SHOOT), _scale)
        self.reload_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.SHORT_BARREL, enums.AnimActions.RELOAD), _scale)
        self.pump_frames = game_controller.load_sprites(constants.get_weapon_frames(enums.Weapons.SHORT_BARREL, enums.AnimActions.PUMP), _scale)
        
        self.reload_end_frame = 8
        self.playing_reload_end = False
        
        self.idle_frame = self.fire_frames[0]
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        self.barrel_offset = vec(0, 7)
        
        self.shoot_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.SHOOT, enums.SFXName.SHORT_BARREL))
        self.empty_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.EMPTY_M, enums.SFXName.EMPTY_1911))
        self.pump_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.PUMP, enums.SFXName.PUMP_SHORT_BARREL))
        self.reload_end_sound = pygame.mixer.Sound(constants.get_sfx(enums.SFXType.WEAPONS,enums.SFXActions.RELOAD, enums.SFXName.SHELL_LOAD_SHORT_BARREL))
   
        self.shoot_sound.set_volume(0.5)
        self.pump_sound.set_volume(0.5)
        self.empty_sound.set_volume(0.1)
        self.reload_end_sound.set_volume(0.5)
        
        self.pumping = False
        self.pumping_frame = 0
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        speed = ((1000/self.reload_delay_ms) / len(self.reload_frames)*2)
        
        if self.firing:
            self.firing = self.fire_anim()
        if self.reloading and not self.pumping:
            self.reload_anim(speed)
        if self.pumping:
            self.pump_anim(speed/2)
    
    def shoot(self, bullet_pos: vec, player_net_id: int):
        if not self.can_shoot() or self.pumping or self.reloading:
            return None
        
        super().shoot(bullet_pos, player_net_id)
        
        self.last_shot_time = datetime.datetime.now()
        self.shoot_sound.play()
        
        bullets = []
        
        for i in range(12):
            _angle = self.weapon_aim_angle + round(random.uniform(-self.dispersion, self.dispersion), 2)
            bullets.append(SmallBullet(bullet_pos, _angle, self.bullet_speed, self.damage, player_net_id, game_controller.get_bullet_id()))
        
        return bullets
    
    
    def reload(self):
        now = datetime.datetime.now()
        # if ran out of ammo
        if self.player_backpack.get_ammo(self.bullet_type) <= 0:
            return False
        # if magazine is full
        if self.magazine_bullets >= self.magazine_size:
            return False
        # if is still reloading
        if (self.reload_start_time != None and now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time) or self.pumping:
            return False
        # if is still firing
        if self.firing:
            return False
        
        
        self.reloading = True
        self.reload_start_time = now
        
    def reload_one(self):
        now = datetime.datetime.now()
        
        # if ran out of ammo
        if self.player_backpack.get_ammo(self.bullet_type) <= 0:
            return False
        # if magazine is full
        if self.magazine_bullets >= self.magazine_size:
            return False
        # if is still reloading
        if (self.reload_start_time != None and now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time) or self.pumping:
            return False
        # if is still firing
        if self.firing:
            return False
        
        self.magazine_bullets += 1
        self.player_backpack.set_ammo(self.player_backpack.get_ammo(self.bullet_type)-1, self.bullet_type)
            
        _will_fit_one_more = self.magazine_bullets +1 <= self.magazine_size and self.player_backpack.get_ammo(self.bullet_type) > 0
        if not _will_fit_one_more:
            self.pumping = True
        return _will_fit_one_more

    def fire_anim(self):
        _still_firing = True
        self.firing_frame += self.fire_rate/10
        
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
            self.reloading = self.reload_one()
                
            self.reloading_frame = 0
            self.playing_reload_end = False
        self.current_frame = self.reload_frames[int(self.reloading_frame)]
        
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)

            
        
            
    