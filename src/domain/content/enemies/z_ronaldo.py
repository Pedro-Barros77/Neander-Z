import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums
from domain.services import game_controller, menu_controller as mc, resources
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle




class ZRonaldo(Enemy):
    def __init__(self, pos,wave, **kwargs):
        kwargs["image_scale"] = 2
        super().__init__(pos, enums.Enemies.Z_RONALDO,wave, **kwargs)
        
        self.damage = kwargs.pop("damage", 15)
        self.name = kwargs.pop("name", f"crawler_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", 30)
        self.hit_frame = 6
        self.hiting = False
        self.attack_box = vec(30,40)
        self.hit_rectangle = None
        self.head_shot_multiplier = 2
        
        _health_rect = self.health_bar.rect.copy()
        _health_rect.width = self.rect.width * 0.6
        self.health_bar.set_rect(_health_rect)
        
        self.kill_score = 60
        self.headshot_score_multiplier = 1.2
        
        self.damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.DEATH), 0.2)
        self.attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.ATTACK), 0.1)
        
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True), name = "zombie_head", id = self.id, owner = self)
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width/3, self.hitbox_head.rect.height - self.rect.height/3)))
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False), name = "zombie_body", id = self.id, owner = self)
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width, self.hitbox_body.rect.height - self.hitbox_head.rect.height/2)))
 
        
    def update(self, **kwargs):
        super().update(**kwargs)
        _head_margin = 15
        if self.hitbox_head != None:
            match self.dir.x:
                case 1:
                    self.hitbox_head.rect.right = self.rect.right - _head_margin
                case -1:
                    self.hitbox_head.rect.left = self.rect.left + _head_margin
        
        if self.running and self.death_time == None:
            self.run_anim(abs(self.speed.x / 7) * mc.dt)
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2 * mc.dt)
        
        if self.dying and self.death_time == None:
            self.dying_anim(0.2 * mc.dt)
            

    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
            
        
        # if self.hit_rectangle != None:
        #     self.hit_rectangle.draw(surface, offset)
        
        # pygame.draw.line(surface, colors.GREEN, vec(self.rect.centerx, self.rect.bottom + 20) - offset ,vec(self.rect.centerx, self.rect.top - 20) - offset)

    def attack(self):
        self.hiting = True
        _hit_rect = pygame.Rect((0,0),self.attack_box)
        _hit_rect.bottom = self.rect.centery
        match self.dir.x:
            case -1:
                _hit_rect.left = self.rect.left
            case 1:
                _hit_rect.right = self.rect.right
            case _:
                _hit_rect.centerx = self.rect.centerx
        
        self.hit_rectangle = Rectangle(self.attack_box, _hit_rect.topleft)
       
        collided = self.attack_collision(self.hit_rectangle)
        if len(collided) > 0:
            for c in collided:
                c.take_damage(self.damage)
                
            rand_sound = random.randint(0, len(self.attack_sounds)-1)
            self.attack_sounds[rand_sound].play()
            
        
    def run_anim(self, speed: float):
       
        self.run_frame += speed
        if self.run_frame > len(self.run_frames)-1:
            self.run_frame = 0
        self.image = game_controller.scale_image(self.run_frames[int(self.run_frame)], self.image_scale)
        if self.speed.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attcking_anim(self, speed: float):
        self.attack_frame += speed
        if int(self.attack_frame) == self.hit_frame - 1 and not self.hiting:
            self.attack()
        if self.attack_frame > len(self.attack_frames)-1:
            self.attack_frame = 0
            self.attacking = False
            self.hiting = False
        self.image = game_controller.scale_image(self.attack_frames[int(self.attack_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def dying_anim(self, speed: float):
        self.death_frame += speed
        if self.death_frame > len(self.death_frames)-1:
            self.death_time = datetime.datetime.now()
            self.death_frame = 0
        else:
            self.image = game_controller.scale_image(self.death_frames[int(self.death_frame)], self.image_scale)
        if self.acceleration.x > 0 and self.death_time == None:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def damage_sound(self):
        sound = self.damage_sounds[random.randint(0, len(self.damage_sounds)-1)]
        if not pygame.mixer.Channel(7).get_busy():
            pygame.mixer.Channel(7).play(sound)
        
    def take_damage(self, value: float, attacker=None, head_shot=False):
        died = super().take_damage(value, attacker, head_shot)
        
        if self.damage_sounds != None and len(self.damage_sounds) > 0:
            self.damage_sound()
        
        if died:
            self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
        
        return died