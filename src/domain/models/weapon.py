import pygame,datetime
from pygame.math import Vector2 as vec


from domain.utils import colors, constants, enums
from domain.services import game_controller, menu_controller
from domain.models.ui.popup_text import Popup
from domain.models.backpack import BackPack

class Weapon(pygame.sprite.Sprite):
    def __init__(self, pos, **kwargs):
        super().__init__()
        
        # The name of the object, for debugging.
        self.name = kwargs.pop("name", "weapon")
        
        self.player_backpack: BackPack = kwargs.pop("backpack", None)
        self.bullet_type: enums.BulletType = kwargs.pop("bullet_type", enums.BulletType.PISTOL)
        
        self.damage = kwargs.pop("damage", 0)
        """The damage of the weapon's bullet."""
        self.bullet_speed = kwargs.pop("bullet_speed", 30)
        """The speed of the weapon's bullet."""
        self.fire_rate = kwargs.pop("fire_rate", 1)
        """The speed of the weapon's bullet."""
        self.magazine_size = 7
        """The magazine capacity of the weapon."""
        self.magazine_bullets = self.magazine_size
        """The number of bullets currently in the magazine."""
        
        self.start_total_ammo = self.player_backpack.get_ammo(self.bullet_type) 
        """The start number of extra bullets."""
        
        self.fire_rate_ratio = 1000
        self.reload_delay_ms = 1000
        
        self.last_shot_time = None
        self.reload_start_time = None
        
        
        self.dir: int = 0
        """The direction that this weapon is pointing to (left: -1, right: 1)."""
        self.last_dir: int = 1
        """The direction that this weapon was pointing to on the last frame (left: -1, right: 1)."""
        
        self.fire_frames = [pygame.Surface((1,1))]
        """The animation frames of this weapon when firing/attacking."""
        _path = kwargs.pop("fire_frames_path", None) 
        if _path != None:
            self.fire_frames = game_controller.load_sprites(_path)
            
        self.idle_frame = self.fire_frames[0]
        """The image of this weapon when not animating."""
            
        self.image = self.idle_frame
        """The surface of this weapon."""
        
        self.current_frame = self.idle_frame
        """The image of the current animation frame, without rotating."""
        

        self.rect = self.image.get_rect()
        """The rect of this weapon."""
        self.rect.topleft = pos
        
        self.firing_frame = 0
        """The current frame of firing animation."""
        self.firing = False
        """If the weapon firing animation is running."""
        self.reloading_frame = 0
        """The current frame of reloading animation."""
        self.reloading = False
        """If the weapon reloading animation is running."""
        
        self.bullet_spawn_offset: vec = kwargs.pop("bullet_spawn_distance", vec(0,0))
        """The distance from the weapon anchor to the barrel, where the bullet will spawn"""
        
        self.weapon_anchor = kwargs.pop("weapon_anchor", vec(0,0))
        """The anchor point of the weapon (the center of the circle it orbits around), relative to the player position"""

        self.weapon_aim_angle: float = 0
        """The angle that the container is rotated along with the weapon."""

        self.shoot_sound: pygame.mixer.Sound = None
        self.empty_sound: pygame.mixer.Sound = None
        self.reload_start_sound: pygame.mixer.Sound = None
        self.reload_end_sound: pygame.mixer.Sound = None

    def shoot(self, bullet_pos: vec, player_net_id: int):
        self.firing = True
        self.magazine_bullets -= 1

    def update(self, **kwargs):
        pass
           
    
           
    def reload(self):
        now = datetime.datetime.now()
        
        # if ran out of ammo
        if self.player_backpack.get_ammo(self.bullet_type) <= 0:
            return
        # if magazine is full
        if self.magazine_bullets >= self.magazine_size:
            return
        # if is still reloading
        if self.reload_start_time != None and now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time:
            return
        # if is still firing
        if self.firing:
            return
        
        self.reloading = True
        self.reload_start_time = now
        
        
        to_load = self.magazine_size - self.magazine_bullets
        diff = self.player_backpack.get_ammo(self.bullet_type) - to_load
        
        if self.reload_start_sound != None:
            self.reload_start_sound.play() 
    
        if diff >= 0:
            self.magazine_bullets += to_load
            self.player_backpack.set_ammo(diff, self.bullet_type)

        else:
            self.magazine_bullets += self.player_backpack.get_ammo(self.bullet_type)
            self.player_backpack.set_ammo(0, self.bullet_type)
  
            
    def can_shoot(self):
        
        # if ran out of ammo
        if self.magazine_bullets <= 0:
            if self.empty_sound != None:
                self.empty_sound.play() 
            return False
        
        _now = datetime.datetime.now()
        
        # if is still reloading
        if self.reload_start_time != None and _now - datetime.timedelta(milliseconds= self.reload_delay_ms) <= self.reload_start_time:
            return
        
        if self.last_shot_time == None:
            self.last_shot_time = _now
            return True
        
        if _now - datetime.timedelta(milliseconds= self.fire_rate_ratio/self.fire_rate) >  self.last_shot_time:
            return True
        
        return False

    