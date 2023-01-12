import pygame, math, datetime, random
from pygame.math import Vector2 as vec

from domain.models.weapon import Weapon
from domain.utils import enums, colors
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle
from domain.services import game_controller, menu_controller as mc, resources

class Melee(Weapon):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        
        self.player_net_id = 0
        
        self.hiting = False
        self.hit_frame = kwargs.pop("hit_frame", 0)
        self.playing_hit_sound = False
        self.hit_rectangle: Rectangle = None
        self.attack_box = kwargs.pop("attack_box", vec(10,10))
        self.magazine_bullets = 1
        
        load_content = kwargs.pop("load_content", True)
        
        if not load_content:
            return
        
        self.attack_frames_1 = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT)+ "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.attack_frames_2 = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT)+ "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.attack_frames_3 = game_controller.load_sprites(resources.get_weapon_path(self.weapon_type, enums.AnimActions.SHOOT)+ "\\03", self.weapon_scale, enums.ConvertType.CONVERT_ALPHA)
        
        self.attack_frames = [self.attack_frames_1, self.attack_frames_2, self.attack_frames_3]
        self.current_attack = 0
        
        self.idle_frame = self.attack_frames_1[0]
        self.image = self.idle_frame
        self.current_frame = self.idle_frame
        
        self.swipe_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.SHOOT) + f'0{i}.mp3') for i in range(1,4)]
        self.hit_sounds = [pygame.mixer.Sound(resources.get_weapon_sfx(self.weapon_type,enums.AnimActions.HIT) + f'0{i}.mp3') for i in range(1,4)]

    def attack_sound(self, hit = False):
        sound = None
        if hit:
            sound = self.hit_sounds[random.randint(0, len(self.hit_sounds)-1)]
        else:
            sound = self.swipe_sounds[random.randint(0, len(self.swipe_sounds)-1)]
        
        sound.play()        
            
    
    def fire_anim(self, speed: float):
        self.firing_frame += speed
        
        if int(self.firing_frame) == self.hit_frame and not self.playing_hit_sound:
            self.attack()
            self.playing_hit_sound = True
        
        if self.firing_frame > len(self.attack_frames[self.current_attack])-1:
            self.firing_frame = 0
            self.firing = False
            self.playing_hit_sound = False
            self.current_frame = self.idle_frame
        else:
            self.current_frame = self.attack_frames[self.current_attack][int(self.firing_frame)]
        
        if self.dir < 0:
            self.current_frame = pygame.transform.flip(self.current_frame, False, True)
    
    def can_shoot(self):
        _now = datetime.datetime.now()
        
        if self.last_shot_time == None:
                self.last_shot_time = _now
                return True
            
        if _now - datetime.timedelta(milliseconds= self.fire_rate_ratio/self.fire_rate) > self.last_shot_time:
            return True
        
        return False
    
    def shoot(self, bullet_pos: vec, player_net_id: int, **kwargs):
        if not self.can_shoot():
            return None
        
        self.player_net_id = player_net_id
        
        self.firing = True
        self.current_attack = random.randint(0, len(self.attack_frames)-1)
        
        self.last_shot_time = datetime.datetime.now()
        
        return None
    
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.firing:
            self.fire_anim(self.fire_rate/5 * mc.dt)
            
    def draw(self, screen: pygame.Surface, offset: vec):
        super().draw(screen, offset)
        
        _attack_hit_rect = pygame.Rect(self.rect.center, self.attack_box)
        if self.dir > 0:
            _attack_hit_rect.left = self.rect.centerx + 3 * self.dir
        elif self.dir < 0:
            _attack_hit_rect.right = self.rect.centerx - 3 * self.dir
        
        self.hit_rectangle = Rectangle(self.attack_box, _attack_hit_rect.topleft + offset)
            
    def attack(self):
        self.hiting = True
        
        collided = self.melee_collision()
        
        self.attack_sound(collided)
        
        return collided
            
    def melee_collision(self):
        for group in game_controller.bullet_target_groups:
            collisions = pygame.sprite.spritecollide(self.hit_rectangle, group, False)
            for c in collisions:
                if isinstance(c, Enemy) or isinstance(c, Rectangle):
                    c.take_damage(self.damage, self.player_net_id)
                return True
        return False
            
    