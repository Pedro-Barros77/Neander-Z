import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums
from domain.services import game_controller, menu_controller as mc, resources, assets_manager
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle

class ZRoger(Enemy):
    def __init__(self, pos,wave, assets_manager: assets_manager.AssetsManager, **kwargs):
        kwargs["image_scale"] = 2
        super().__init__(pos, enums.Enemies.Z_ROGER,wave,assets_manager, **kwargs)
        
        self.damage = kwargs.pop("damage", 15)
        self.name = kwargs.pop("name", f"zombie_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_frame_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", 30)
        self.hit_frame = 8
        self.hiting = False
        self.attack_box = vec(50,15)
        self.hit_rectangle = None
        self.head_shot_multiplier = kwargs.pop("head_shot_multiplier", 2)
        
        self.kill_score = kwargs.pop("kill_score", 53)
        self.headshot_score_multiplier = kwargs.pop("headshot_score_multiplier", 1.5)
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True), name = "zombie_head", id = self.id, owner = self)
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width, self.hitbox_head.rect.height - self.rect.height/1.5)))
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False), name = "zombie_body", id = self.id, owner = self)
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width, self.hitbox_body.rect.height - self.hitbox_head.rect.height)))
 
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if self.running and self.death_time == None:
            self.run_anim(abs(self.speed.x / 5) * mc.dt)
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2 * mc.dt)
        
        if self.dying and self.death_time == None:
            self.dying_anim(0.2 * mc.dt)
            
    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
        
        


    def attack(self):
        self.hiting = True
        _rect = pygame.Rect((0,0), self.attack_box)
        _rect.centerx = self.rect.centerx + 12 + (5*self.dir.x)
        _rect.top = self.rect.centery - 20
        self.hit_rectangle = Rectangle(_rect.size, _rect.topleft)

        collided = self.attack_collision(self.hit_rectangle)
        if len(collided) > 0:
            for c in collided:
                c.take_damage(self.damage)
            
            rand_sound = random.randint(0, len(self.get_sounds(enums.AnimActions.ATTACK))-1)
            self.get_sounds(enums.AnimActions.ATTACK)[rand_sound].play()
            
        
    def run_anim(self, speed: float):
       
        self.run_frame += speed
        if self.run_frame > len(self.get_frames(enums.AnimActions.RUN))-1:
            self.run_frame = 0
        self.image = game_controller.scale_image(self.get_frames(enums.AnimActions.RUN)[int(self.run_frame)], self.image_scale)
        if self.speed.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attcking_anim(self, speed: float):
        self.attack_frame += speed
        if int(self.attack_frame) == self.hit_frame - 1 and not self.hiting:
            self.attack()
        if self.attack_frame > len(self.get_frames(enums.AnimActions.ATTACK))-1:
            self.attack_frame = 0
            self.attacking = False
            self.hiting = False
        self.image = game_controller.scale_image(self.get_frames(enums.AnimActions.ATTACK)[int(self.attack_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def dying_anim(self, speed: float):
        self.death_frame += speed
        if self.death_frame > len(self.get_frames(enums.AnimActions.DEATH))-1:
            self.death_time = datetime.datetime.now()
            self.death_frame = 0
        else:
            self.image = game_controller.scale_image(self.get_frames(enums.AnimActions.DEATH)[int(self.death_frame)], self.image_scale)
        if self.dir.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
        
    def damage_sound(self):
        sound = self.get_sounds(enums.AnimActions.TAKE_DAMAGE)[random.randint(0, len(self.get_sounds(enums.AnimActions.TAKE_DAMAGE))-1)]
        if not pygame.mixer.Channel(7).get_busy():
            pygame.mixer.Channel(7).play(sound)
        
    def take_damage(self, value: float, attacker=None, head_shot=False):
        died = super().take_damage(value, attacker, head_shot)
        
        if self.get_sounds(enums.AnimActions.TAKE_DAMAGE) != None and len(self.get_sounds(enums.AnimActions.TAKE_DAMAGE)) > 0:
            self.damage_sound()
        
        if died:
            self.get_sounds(enums.AnimActions.DEATH)[random.randint(0, len(self.get_sounds(enums.AnimActions.DEATH))-1)].play()
        
        return died