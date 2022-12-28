import pygame, math, datetime
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import constants
from domain.content.weapons.small_bullet import SmallBullet
from domain.services import game_controller
class Pistol(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.damage = 5
        self.bullet_speed = 30
        self.fire_rate = 5.5
        self.last_shot_time = None
        self.magazine_size = 7
        self.magazine_bullets = self.magazine_size
        self.total_ammo = 30
        
        self.reload_frames = []
        """The animation frames of this weapon when reloading."""
        
        self.barrel_offset = vec(0, 7)
        
        self.shoot_sound = pygame.mixer.Sound(f'{constants.SOUNDS_PATH}sound_effects\\1911.mp3')
        self.shoot_sound.set_volume(0.1)
        
    
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
    
    def reload_anim(self):
        pass

    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.firing:
            self.firing = self.fire_anim()
            
    