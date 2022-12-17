import pygame

from pygame.math import Vector2 as vec


from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller
from domain.models.weapon import Weapon
from domain.models.progress_bar import ProgressBar



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, **kwargs):
        super().__init__()
        self.screen_size: vec = vec(kwargs.pop("screen_size", vec(500,500)))
        self.net_id = kwargs.pop("net_id", 0)
        self.jump_force = kwargs.pop("jump_force", 12)
        self.name = kwargs.pop("name", "player")
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.grounded = False
        self.health = 100
        
        self.image_scale = 2
        
        self.image = game_controller.scale_image(pygame.image.load(image), self.image_scale)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        # The adjustment that every object should do to their position so the camera is centered on the player.
        self.offset_camera = vec(0,0)
        
        self.last_rect = self.rect.copy()
        
        self.weapon_container: pygame.Surface = pygame.Surface((1,1))
        self.weapon_container_rect: pygame.Rect = pygame.Rect((0,0),(1,1))
        self.weapon_container_angle: float = 0
        self.player2_mouse_pos: vec = vec(0,0)
        self.player2_offset_camera: vec = vec(0,0)
        
        self.firing = False
        self.current_weapon = Weapon((self.rect.width, self.rect.centery), fire_frames_path = constants.PISTOL_FOLDER)
        
        self.turning_dir = 0
        self.turning_frame = 0
        turn_folder = constants.get_character_frames(constants.Characters.CARLOS, constants.Actions.TURN)
        self.turn_frames = game_controller.load_sprites(turn_folder)
        
        self.jumping = False
        self.jumping_frame = 0
        jump_folder = constants.get_character_frames(constants.Characters.CARLOS, constants.Actions.JUMP)
        self.jump_frames = game_controller.load_sprites(jump_folder)
        self.jump_frames.append(self.jump_frames[-1])
        
        self.running = False
        self.running_frame = 0
        run_folder = constants.get_character_frames(constants.Characters.CARLOS, constants.Actions.RUN)
        self.run_frames = game_controller.load_sprites(run_folder)
        
        self.falling_ground = False
        self.falling_ground_frame = 0
        fall_ground_folder = constants.get_character_frames(constants.Characters.CARLOS, constants.Actions.FALL_GROUND)
        self.fall_ground_frames = game_controller.load_sprites(fall_ground_folder)
        
        self.health_bar: ProgressBar = None
        
        if self.name == "P1":
            self.health_bar = ProgressBar(self.health, pygame.Rect((10, 10), (self.screen_size.x/2, 20)), hide_on_full = False)
        else:
            self.health_bar = ProgressBar(self.health, pygame.Rect((self.rect.left, self.rect.top), (self.rect.width * 1.3, 8)))
        
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
    
    # called each frame
    def update(self):
        if self.name == "P1":
            _mouse_target = vec(pygame.mouse.get_pos())
            _offset_camera_target = self.offset_camera
        else:
            _mouse_target = self.player2_mouse_pos
            _offset_camera_target = vec(0,0)
            self.health_bar.rect.centerx = self.rect.centerx
            self.health_bar.rect.top = self.rect.top - 15
            
        self.health_bar.update()
            
        _size = vec(self.current_weapon.rect.size)
        _offset = vec(30,30)
        
        _wrapper = pygame.Surface(_size*2 + vec(self.rect.size) + _offset)
        _wrapper = _wrapper.convert_alpha()
        _wrapper.fill((0, 0, 0, 0))
        _rect = _wrapper.get_rect()
        _rect.center = vec(self.rect.center) - _offset_camera_target
        _wrapper.blit(self.current_weapon.image, vec(_size.x + self.rect.width + _offset.x, self.rect.height/2 + _offset.y))
        
        if self.name == "P1":
            img, rec, angle = game_controller.rotate_to_mouse(_wrapper, vec(_rect.center), _mouse_target)
        else:
            img, rec, angle = game_controller.rotate_to_angle(_wrapper, vec(_rect.center), self.weapon_container_angle)
            
        self.weapon_container = img
        self.weapon_container_rect = rec
        self.weapon_container_angle = angle
        
        _gun_pos = vec(self.current_weapon.rect.center) + self.pos - _offset_camera_target
        def flip():
            self.current_weapon.image = pygame.transform.flip(self.current_weapon.image, False, True)
            self.current_weapon.last_dir = self.current_weapon.dir.copy()
    
        _flip_margin = 0
        if _mouse_target.x < _gun_pos.x - _flip_margin:
            self.current_weapon.dir.x = -1
            if self.current_weapon.last_dir.x > self.current_weapon.dir.x:
                flip()
        elif _mouse_target.x > _gun_pos.x + _flip_margin:
            self.current_weapon.dir.x = 1
            if self.current_weapon.last_dir.x < self.current_weapon.dir.x:
                flip()
        else:
            self.current_weapon.dir.x = 0
        
        self.current_weapon.update()
        
        if self.turning_dir != 0:
            self.turn_anim(0.3)
        if self.falling_ground:
            self.fall_ground_anim(0.2)
        if self.running:
            self.run_anim(abs(self.speed.x / 26.4))
        if self.jumping:
            self.jump_anim(0.2)
        _still_firing = False
        if self.firing:
            _still_firing = self.current_weapon.fire_anim()
            self.firing = _still_firing
        if not _still_firing:
            self.current_weapon.image = self.current_weapon.idle_frame
        
    def draw(self, surface: pygame.Surface, offset: vec):
        surface.blit(self.image, self.pos - offset)
        if self.name == "P1":
            surface.blit(self.weapon_container, vec(self.weapon_container_rect.topleft))
        else:
            surface.blit(self.weapon_container, vec(self.weapon_container_rect.topleft) - offset)
            
        self.health_bar.draw(surface)
        
    def shoot(self):
        self.firing = True
        
    def turn_anim(self, speed: float):
        self.turning_frame = math.clamp(self.turning_frame + (speed * self.turning_dir), 0, len(self.turn_frames)-1)
        
        if self.turning_frame == len(self.turn_frames)-1:
            self.running = True if self.turning_dir != 0 else False
            self.turning_dir = 0
        self.image = game_controller.scale_image(self.turn_frames[int(self.turning_frame)], self.image_scale)
        if self.turning_dir > 0 and self.acceleration.x > 0 or\
           self.turning_dir < 0 and self.acceleration.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def jump_anim(self, speed: float):
        if self.jumping_frame > len(self.jump_frames):
            self.jumping_frame = 0
            self.jumping = False
            # self.speed.y = -self.jump_force
        self.image = game_controller.scale_image(self.jump_frames[int(self.jumping_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.jumping_frame += speed
    
    def fall_ground_anim(self, speed: float):
        if self.falling_ground_frame > len(self.fall_ground_frames)-1:
            self.image = game_controller.scale_image(self.fall_ground_frames[int(len(self.fall_ground_frames)-1)], self.image_scale)
            self.falling_ground_frame = 0
            self.falling_ground = False
            return
        self.image = game_controller.scale_image(self.fall_ground_frames[int(self.falling_ground_frame)], self.image_scale)
        self.falling_ground_frame += speed
        
    def run_anim(self, speed: float):
        self.running_frame += speed
        
        if self.running_frame > len(self.run_frames)-1:
            self.running_frame = 0
        self.image = game_controller.scale_image(self.run_frames[int(self.running_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def take_damage(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health - value, 0, self.health_bar.max_value)
        self.health_bar.remove_value(value)
        
    def get_health(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health + value, 0, self.health_bar.max_value)
        self.health_bar.add_value(value)