import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller, menu_controller as mc, resources, assets_manager
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle




class ZRaven(Enemy):
    def __init__(self, pos,wave,assets_manager: assets_manager.AssetsManager, **kwargs):
        kwargs["image_scale"] = 0.4
        super().__init__(pos, enums.Enemies.Z_RAVEN, wave, assets_manager, **kwargs)
        
        self.damage = kwargs.pop("damage", 5)
        self.name = kwargs.pop("name", f"raven_1")
        
        self.pos: vec = vec((pos))
        self.start_pos = self.pos.copy()
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_frame_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", 30)
        self.dive_attack_distance = kwargs.pop("dive_attack_distance", 200)
        self.hit_frame = 7
        self.hiting = False
        self.attack_box = vec(15,15)
        self.hit_rectangle = None
        self.head_shot_multiplier = kwargs.pop("head_shot_multiplier", 2)
        
        self.hover_height = 400
        self.hovering = True
        self.diving = False
        self.rising = False
        self.hover_dir = self.dir.x
        
        self.attack_timer_ms = kwargs.pop("attack_timer_ms", 3000)
        self.attack_chance = kwargs.pop("attack_chance", 0.3)
        self.last_attack_attempt = datetime.datetime.now()
        
        self.kill_score = kwargs.pop("kill_score", 20)
        self.headshot_score_multiplier = kwargs.pop("headshot_score_multiplier", 1.8)
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True), name = "zombie_head", id = self.id, owner = self)
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width/5, self.hitbox_head.rect.height/5)))
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False), name = "zombie_body", id = self.id, owner = self)
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width/3, self.hitbox_body.rect.height/3)))

        self.hight_set = False
        
    def update(self, **kwargs):
        
        _hover_y = self.start_pos.y - self.hover_height
        
        if not self.hight_set:
            self.pos.y = _hover_y
            self.update_rect()
            self.hight_set = True
            
        self.health_bar.update()
        
        if self.hitbox_head != None:
            self.hitbox_head.rect.top = self.rect.top + self.rect.height/2.4
            _h_margin = self.rect.width/5
            match self.dir.x:
                case 1:
                    self.hitbox_head.rect.right = self.rect.right - _h_margin
                case -1:
                    self.hitbox_head.rect.left = self.rect.left + _h_margin
            self.hitbox_head.update_pos()
            
        if self.hitbox_body != None:
            self.hitbox_body.rect.top = self.rect.top + self.rect.height/3
            _h_margin = self.rect.width/5 + self.hitbox_head.rect.width
            match self.dir.x:
                case 1:
                    self.hitbox_body.rect.right = self.rect.right - _h_margin
                case -1:
                    self.hitbox_body.rect.left = self.rect.left + _h_margin
                    
            self.hitbox_body.update_pos()
            
            
        if not self.is_alive and self.death_time != None:
            self.fade_out_anim()
            
        if self.dying and self.death_time == None:
            self.dying_anim(0.2 * mc.dt)
            
        if not self.is_alive or self.dying or self.death_time != None:
            return
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_frame_dir = self.dir.copy()
            self.speed.x = 0
            
        
        if self.hovering or self.rising:
            #if is out of flight range
            if self.dir.x == 1 and self.rect.centerx > player_center.x + self.dive_attack_distance or \
                self.dir.x == -1 and self.rect.centerx < player_center.x - self.dive_attack_distance:
                self.dir.x = 0
            
            #the min speed to reach before turning around
            _turn_margin = self.movement_speed / 2
                
            # if stoped moving
            if self.dir.x == 0:
                #if was moving to the right
                if self.hover_dir == 1:
                    #if it's slow enought to turn arround
                    if self.speed.x < _turn_margin:
                        self.dir.x = -1
                        self.hover_dir = -1
                        if self.last_frame_dir.x > self.dir.x:
                            self.changed_hover_dir = True
                            flip()
                    
                #if was moving to the left     
                elif self.hover_dir == -1:
                    #if it's slow enought to turn arround
                    if self.speed.x > -_turn_margin:
                        self.dir.x = 1
                        self.hover_dir = 1
                        if self.last_frame_dir.x < self.dir.x:
                            self.changed_hover_dir = True
                            flip()
            
            if self.rect.top < _hover_y and self.speed.y < _turn_margin/5:
                self.dir.y = 1
            elif not self.rising:
                self.dir.y = 0
                
        self.acceleration.x = 0
        self.acceleration.y = 0
        self.last_rect = self.rect.copy()
        
        # fix Movement
        if self.dir.x != 0:
            self.acceleration.x = self.movement_speed * self.dir.x
        if not self.attacking and not self.dying:
            self.acceleration.x += self.speed.x * game.friction
            self.speed.x += self.acceleration.x * mc.dt
            self.pos.x += (self.speed.x + 0.5 * self.acceleration.x) * mc.dt
            
        if self.dir.y != 0:
            self.acceleration.y = self.movement_speed * 1.3 * self.dir.y
        if not self.dying:
            self.acceleration.y += self.speed.y * game.friction
            self.speed.y += self.acceleration.y * mc.dt
            self.pos.y += (self.speed.y + 0.5 * self.acceleration.y) * mc.dt
            
        self.update_rect()
        
        attack = self.try_attack()
        _in_dive_range = abs(self.rect.centerx - player.rect.centerx) < self.dive_attack_distance
        
        if not self.rising and _in_dive_range and (attack or self.diving):
            self.fly_to(player.rect)
            
        if self.rect.top > player.rect.top:
            self.hovering = False
            self.rising = True
            self.diving = False
        
        if self.rising:
            self.fly_back()
            
        #animations
        
        if self.running and self.death_time == None:
            self.run_anim(abs((2.5 - self.speed.y/3) / 10) * mc.dt)
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2 * mc.dt)

            
    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
        
        # self.blit_debug = True
        # self.draw_blit_debug(surface, offset)
    
    def draw_blit_debug(self, screen: pygame.Surface, offset: vec):
        if self.hitbox_head != None:
            self.hitbox_head.draw(screen, offset)
        if self.hitbox_body != None:
            self.hitbox_body.draw(screen, offset)
        
        if self.hit_rectangle != None:
            self.hit_rectangle.draw(screen, offset)
        
        pygame.draw.rect(screen, colors.BLUE, math.rect_offset(self.rect, -offset), 1)
        pygame.draw.line(screen, colors.GREEN, vec(self.rect.centerx, self.rect.bottom + 20) - offset,vec(self.rect.centerx, self.rect.top - 20) - offset)

    def try_attack(self):
        _now = datetime.datetime.now()
        if _now > self.last_attack_attempt + datetime.timedelta(milliseconds=self.attack_timer_ms):
            _attack = random.random() < self.attack_chance
            self.last_attack_attempt = _now
            return _attack
        
        return False
    
    def fly_back(self):
        self.hovering = False
        self.rising = True
        self.diving = False

        if self.rect.top > self.start_pos.y - self.hover_height:
            self.dir.y = -1
        else:
            self.dir.y = 0
            self.hovering = True
            self.rising = False
            self.diving = False
        
    def fly_to(self, target: pygame.Rect):
        
        if not self.diving:
            _rand = random.randint(0, len(self.get_sounds(enums.AnimActions.DASH))-1)
            self.get_sounds(enums.AnimActions.DASH)[_rand].play()
        
        self.hovering = False
        self.rising = False
        self.diving = True
        
        if self.rect.centery < target.top - self.rect.height/2:
            self.dir.y = 1
        else:
            self.dir.y = 0
            self.hovering = False
            self.rising = False
            self.diving = False
            
            _distance = abs(self.rect.centerx - target.centerx)
            if _distance <= self.attack_distance:
                
                self.attacking = True
            else:
                self.rising = True
                
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_frame_dir = self.dir.copy()
            self.speed.x = 0
        
        # flip
        if target.centerx < self.rect.centerx - self.image_flip_margin:
            self.dir.x = -1
            if self.last_frame_dir.x > self.dir.x:
                flip()
        elif target.centerx > self.rect.centerx + self.image_flip_margin:
            self.dir.x = 1
            if self.last_frame_dir.x < self.dir.x:
                flip()
        else:
            self.dir.x = 0
            
            
    def attack(self):
        self.hiting = True
        _hit_rect = pygame.Rect((0,0),self.attack_box)
        _hit_rect.bottom = self.rect.bottom
        _hit_rect.centerx = self.rect.centerx + self.attack_box.x * self.dir.x
        
        self.hit_rectangle = Rectangle(self.attack_box, _hit_rect.topleft)
        
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
            self.rising = True
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