import pygame

from pygame.math import Vector2 as vec


from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.weapon import Weapon



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, **kwargs):
        super().__init__()
        self.net_id = kwargs.pop("net_id", 0)
        self.jump_force = kwargs.pop("jump_force", 12)
        self.name = kwargs.pop("name", "player")
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        
        self.image = game_controller.scale_image(pygame.image.load(image), 2)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        # The adjustment that every object should do to their position so the camera is centered on the player.
        self.offset_camera = vec(0,0)
        
        self.last_rect = self.rect.copy()
        
        self.current_weapon: Weapon = None
        self.weapon_container: pygame.Surface = None
        self.weapon_container_rect: pygame.Rect = None
        self.weapon_container_angle: float = 0
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
    
    # called each frame
    def update(self):
        
        _size = vec(self.current_weapon.rect.size)
        _offset = vec(30,30)
        
        _wrapper = pygame.Surface(_size*2 + vec(self.rect.size) + _offset)
        _wrapper = _wrapper.convert_alpha()
        _wrapper.fill((0, 0, 0, 0))
        _rect = _wrapper.get_rect()
        _rect.center = vec(self.rect.center) - self.offset_camera
        _wrapper.blit(self.current_weapon.image, vec(_size.x + self.rect.width + _offset.x, self.rect.height/2 + _offset.y))
        img, rec, angle = game_controller.rotate_to_mouse(_wrapper, vec(_rect.center))
        self.weapon_container = img
        self.weapon_container_rect = rec
        self.weapon_container_angle = angle
        
        _mouse_pos = vec(pygame.mouse.get_pos())
        _gun_pos = vec(self.current_weapon.rect.center) + self.pos - self.offset_camera
        def flip():
            self.current_weapon.image = pygame.transform.flip(self.current_weapon.image, False, True)
            self.current_weapon.last_dir = self.current_weapon.dir.copy()
    
        _flip_margin = 0
        if _mouse_pos.x < _gun_pos.x - _flip_margin:
            self.current_weapon.dir.x = -1
            if self.current_weapon.last_dir.x > self.current_weapon.dir.x:
                flip()
        elif _mouse_pos.x > _gun_pos.x + _flip_margin:
            self.current_weapon.dir.x = 1
            if self.current_weapon.last_dir.x < self.current_weapon.dir.x:
                flip()
        else:
            self.current_weapon.dir.x = 0
        
        self.current_weapon.update()
        
        print(self.weapon_container_angle)
        
        
    def shoot(self):
        self.current_weapon.firing = True