import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller, menu_controller as mc, resources, assets_manager
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle




class ZRui(Enemy):
    def __init__(self, pos,wave,assets_manager: assets_manager.AssetsManager, **kwargs):
        kwargs["image_scale"] = 2
        super().__init__(pos, enums.Enemies.Z_RUI,wave, assets_manager, **kwargs)
        
        self.damage = kwargs.pop("damage", 15)
        self.name = kwargs.pop("name", f"boss_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_frame_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", self.rect.width/2.2 )
        self.attack_hit_frame = 10
        self.bump_hit_frame = 4
        self.hiting = False
        self.attack_box = vec(220,60)
        self.bump_box = vec(100,200)
        self.hit_rectangle = None
        self.head_shot_multiplier = kwargs.pop("head_shot_multiplier", 2)
        self.bump_knockback_force = 50
        self.attack_knockback_force = 20
        
        self.kill_score = kwargs.pop("kill_score", 310)
        self.headshot_score_multiplier = kwargs.pop("headshot_score_multiplier", 2)
        
        _health_rect = self.health_bar.rect.copy()
        _health_rect.width = self.rect.width * 0.4
        _health_rect.bottom = 0
        self.health_bar.set_rect(_health_rect)
        self.health_bar.value_anim_speed = 0.55
        
        self.attack_frames = None
        self.bumping = False
        self.bump_frame = 0
        self.bump_damage_multiplier = 0.3
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True), name = "zombie_head", id = self.id, owner = self)
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width/8, self.hitbox_head.rect.height - self.rect.height/1.4)))
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False), name = "zombie_body", id = self.id, owner = self)
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width / 3.8, self.hitbox_body.rect.height - self.hitbox_head.rect.height*1.5)))

        self.bump_distance = kwargs.pop("bump_distance", self.hitbox_body.rect.width/1.8)
        
    def update(self, **kwargs):
        kwargs["attack"] = False
        super().update(**kwargs)
        
        if self.hitbox_head != None:
            self.hitbox_head.rect.centerx = self.rect.centerx
            self.hitbox_head.rect.top = self.rect.top + self.rect.height/3.4
        if self.hitbox_body != None:
            self.hitbox_body.rect.centerx = self.rect.centerx
            self.hitbox_body.rect.bottom = self.rect.bottom
            
        
        if self.dying and self.death_time == None:
            self.dying_anim(0.2 * mc.dt)
        if not self.is_alive or self.dying or self.death_time != None:
            return
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        
        _player_distance = abs(player_center.x - self.hitbox_body.rect.centerx)
        _attack_distance = _player_distance <= self.attack_distance
        _bump_distance = _player_distance <= self.bump_distance
        
        if _attack_distance and not self.attacking and not self.bumping and not _bump_distance:
            self.attacking = True
            self.bumping = False
        elif _bump_distance and not self.bumping and not self.attacking:
            self.bumping = True
            self.attacking = False
        
        
        
        if self.running and self.death_time == None:
            self.run_anim(abs(self.speed.x / 4.5) * mc.dt)
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2 * mc.dt)
            
        if self.bumping and self.death_time == None:
            self.bump_anim(0.2 * mc.dt)
            
            
    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
        
        # if self.hitbox_head != None:
        #     self.hitbox_head.draw(surface, offset)
        # if self.hitbox_body != None:
        #     self.hitbox_body.draw(surface, offset)
        
        # if self.hit_rectangle != None:
        #     self.hit_rectangle.draw(surface, offset)
            
        # pygame.draw.rect(surface, colors.RED, math.rect_offset(self.rect, -offset), 5)


    def attack(self, atk_number: int):
        self.hiting = True
        _knockback = vec(0,0)
        _sound = None
        _damage = 0
        match atk_number:
            case 1:
                _knockback = vec(self.attack_knockback_force, 0)
                _atk_rect = pygame.Rect((0,0), self.attack_box)
                rand_sound = random.randint(0, len(self.get_sounds(enums.AnimActions.ATTACK))-1)
                _sound = self.get_sounds(enums.AnimActions.ATTACK)[rand_sound]
                _damage = self.damage
            
                if self.dir.x < 0:
                    _atk_rect.right = self.hitbox_body.rect.left
                    _knockback.x *= -1
                elif self.dir.x > 0:
                    _atk_rect.left = self.hitbox_body.rect.right
                else:
                    _atk_rect.right = self.hitbox_body.rect.left
                    _knockback.x *= -1
            case 2:
                _knockback = vec(self.bump_knockback_force, self.bump_knockback_force/4)
                _atk_rect = pygame.Rect((0,0), self.bump_box)
                rand_sound = random.randint(0, len(self.get_sounds(enums.AnimActions.BUMP))-1)
                _sound = self.get_sounds(enums.AnimActions.BUMP)[rand_sound]
                _damage = self.damage * self.bump_damage_multiplier
            
                if self.dir.x < 0:
                    _atk_rect.centerx = self.hitbox_body.rect.left
                    _knockback.x *= -1
                elif self.dir.x > 0:
                    _atk_rect.centerx = self.hitbox_body.rect.right
                else:
                    _atk_rect.centerx = self.hitbox_body.rect.centerx
                    _knockback.x *= -1
                    
                    
        _atk_rect.bottom = self.rect.bottom

        self.hit_rectangle = Rectangle(_atk_rect.size, _atk_rect.topleft)
       
        _sound.play()
            
            
            
        collided = self.attack_collision(self.hit_rectangle)
        if len(collided) > 0:
            for c in collided:
                c.take_damage(_damage)
                c.speed.x += _knockback.x
                c.speed.y -= _knockback.y
            
            
        
    def run_anim(self, speed: float):
       
        self.run_frame += speed
        if self.run_frame > len(self.get_frames(enums.AnimActions.RUN))-1:
            self.run_frame = 0
        self.image = game_controller.scale_image(self.get_frames(enums.AnimActions.RUN)[int(self.run_frame)], self.image_scale)
        if self.speed.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attcking_anim(self, speed: float):
        self.attack_frame += speed
        if int(self.attack_frame) == self.attack_hit_frame - 1 and not self.hiting:
            self.attack(1)
        if self.attack_frame > len(self.get_frames("attack_frames1"))-1:
            self.attack_frame = 0
            self.attacking = False
            self.hiting = False
        self.image = game_controller.scale_image(self.get_frames("attack_frames1")[int(self.attack_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def bump_anim(self, speed: float):
        self.bump_frame += speed
        if int(self.bump_frame) == self.bump_hit_frame - 1 and not self.hiting:
            self.attack(2)
        if self.bump_frame > len(self.get_frames("attack_frames2"))-1:
            self.bump_frame = 0
            self.bumping = False
            self.hiting = False
        self.image = game_controller.scale_image(self.get_frames("attack_frames2")[int(self.bump_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def dying_anim(self, speed: float):
        self.death_frame += speed
        if self.death_frame > len(self.get_frames(enums.AnimActions.DEATH))-1:
            self.death_time = datetime.datetime.now()
            self.death_frame = 0
        else:
            self.image = game_controller.scale_image(self.get_frames(enums.AnimActions.DEATH)[int(self.death_frame)], self.image_scale)
        if self.dir.x > 0 and self.death_time == None:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def damage_sound(self):
        sound = self.get_sounds(enums.AnimActions.TAKE_DAMAGE)[random.randint(0, len(self.get_sounds(enums.AnimActions.TAKE_DAMAGE))-1)]
        if not pygame.mixer.Channel(7).get_busy():
            pygame.mixer.Channel(7).play(sound)
        
    def take_damage(self, value: float, attacker=None, head_shot=False):
        died = super().take_damage(value, attacker, head_shot)
        
        self.damage_sound()
        
        if died:
            self.get_sounds(enums.AnimActions.DEATH)[random.randint(0, len(self.get_sounds(enums.AnimActions.DEATH))-1)].play()
        
        return died