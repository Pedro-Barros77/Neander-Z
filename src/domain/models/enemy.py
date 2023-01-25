import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants, math_utillity as math
from domain.services import game_controller, menu_controller as mc, resources, assets_manager
from domain.models.progress_bar import ProgressBar
from domain.models.ui.popup_text import Popup
from domain.models.rectangle_sprite import Rectangle



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_name: enums.Enemies, wave, assets_manager: assets_manager.AssetsManager, **kwargs):
        super().__init__()
        
        self.assets_manager = assets_manager
        self.id = kwargs.pop("id", 0)
        self.name = "enemy"
        self.wave = wave
        self.jump_force = 12
        self.damage = 1
        self.enemy_name = enemy_name
        self.image_scale = kwargs.pop("image_scale", 1)
        self.movement_speed = kwargs.pop("movement_speed", 0.1)
        self.health = kwargs.pop("health", 30)
        self.start_health = self.health
        self.head_shot_multiplier = kwargs.pop("head_shot_multiplier", 2)
        self.attack_targets = game_controller.enemy_target_groups
        self.client_type = enums.ClientType.UNDEFINED
        
        self.headshot_score_multiplier = kwargs.pop("headshot_score_multiplier", 2)
        self.kill_score = kwargs.pop("kill_score", 10)

        self.killer = 0
        self.headshot_kill = False
        self.death_time: datetime.datetime = None
        self.fade_out_ms = 1000
        self.image_alpha = 255
        self.death_callback: function = kwargs.pop("death_callback", None)
        
        self.pos: vec = vec((pos))
        self.speed = vec(0,0)
        self.acceleration: vec = vec(0,0)
        self.dir: vec = vec(0,0)
        self.last_frame_dir: vec = self.dir.copy()
        self.grounded = False
        
        self.is_alive = True
        
        self.running = True
        """If the running animation is running."""
        self.run_frame = 0
        """The current frame index of the running animation."""
        
        self.attacking = False
        self.attack_frame = 0

        self.dying = False
        self.death_frame = 0
        
        self.image = game_controller.scale_image(pygame.image.load(resources.get_enemy_path(self.enemy_name, enums.AnimActions.IDLE)), self.image_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.size = self.image.get_size()
        
        self.attack_start_sounds: list[pygame.mixer.Sound] = None
        self.attack_sounds: list[pygame.mixer.Sound] = None
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.image_flip_margin = 10
        self.player_offset = vec(0,0)
        
        self.last_rect = self.rect.copy()
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, owner = self)
        self.hitbox_head: Rectangle = None
        
        self.health_bar = ProgressBar(self.health, pygame.Rect(self.pos - vec(0,-15), (self.rect.width * 1.3, 7)), 
                border_width = 1, 
                border_color = colors.LIGHT_GRAY, 
                value_anim_speed = 0.2)
        
        #debug
        self.blit_debug = False
    
    def get_closest_player(self, p1, p2):
        if p2 == None:
            return p1
        
        closest = sorted([p1, p2], key= lambda p: vec(p.rect.center).distance_to(vec(self.rect.center)))[0]
        return closest

    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
    
    def client_update(self, **kwargs):
        if not self.is_alive or self.dying:
            return
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            
        if self.last_frame_dir.x > self.dir.x:
            flip()
        if self.last_frame_dir.x < self.dir.x:
            flip()
            
        if abs(player_center.x - self.rect.centerx) <= self.attack_distance and player.rect.bottom > self.rect.top:
            self.attacking = True
        
        
            
    def host_update(self, **kwargs):
        if not self.is_alive or self.dying or self.death_time != None:
            return
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_frame_dir = self.dir.copy()
            self.speed.x = 0
        
        
        if player_center.x < self.rect.centerx - self.image_flip_margin:
            self.dir.x = -1
            if self.last_frame_dir.x > self.dir.x:
                flip()
        elif player_center.x > self.rect.centerx + self.image_flip_margin:
            self.dir.x = 1
            if self.last_frame_dir.x < self.dir.x:
                flip()
        else:
            self.dir.x = 0
            
        self.acceleration.x = 0
        self.last_rect = self.rect.copy()
        
        has_attack_range = abs(player_center.x - self.rect.centerx) <= self.attack_distance and player.rect.bottom > self.rect.top
        
        # Movement
        if self.dir.x != 0:
            self.acceleration.x = self.movement_speed * self.dir.x
        if not self.attacking and not self.dying and not has_attack_range:
            self.acceleration.x += self.speed.x * game.friction
            self.speed.x += self.acceleration.x * mc.dt
            self.pos.x += (self.speed.x + 0.5 * self.acceleration.x) * mc.dt
        
        # Gravity
        game.apply_gravity(self)
        self.update_rect()
        
        # jump
        self.grounded = self.collision(game, game.collision_group, enums.Orientation.VERTICAL)
        # if self.dir.y > 0 and self.grounded:
        #     self.speed.y = - self.jump_force
        # solid collision
        self.collision(game, game.collision_group, enums.Orientation.HORIZONTAL, self.hitbox_body if self.hitbox_body != None else self)

        _should_attack = kwargs.pop("attack", True)

        if has_attack_range and _should_attack:
            if self.attack_start_sounds != None and not self.attacking:
                rand_sound = random.randint(0, len(self.attack_start_sounds)-1)
                self.attack_start_sounds[rand_sound].play()
            self.attacking = True

        
    
    
    def update(self, **kwargs):
        self.client_type = kwargs.pop("client_type", enums.ClientType.UNDEFINED)
        self.health_bar.update()
        
        if self.hitbox_head != None:
            self.hitbox_head.rect.topleft = self.pos
            self.hitbox_head.update_pos()
        if self.hitbox_body != None:
            self.hitbox_body.rect.topleft = self.pos if self.hitbox_head == None else self.hitbox_head.rect.bottomleft
            self.hitbox_body.update_pos()
            
        if not self.is_alive and self.death_time != None:
            self.fade_out_anim()
        if self.client_type == enums.ClientType.GUEST:
            self.client_update(**kwargs)
        else:
            self.host_update(**kwargs)
        
        

       
    def draw(self, surface: pygame.Surface, offset: vec):
        _result = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        _result.blit(self.image, (0,0))
        _result.set_alpha(self.image_alpha)
        surface.blit(_result, self.pos - offset)
        
        # self.blit_debug = True
        # pygame.draw.rect(surface, colors.BLUE, math.rect_offset(self.rect, -offset), 1)



        self.health_bar.rect.center = vec(self.rect.centerx, self.rect.top - 15) - offset
        _result_health_bar = pygame.Surface(self.health_bar.image.get_size(), pygame.SRCALPHA)
        _result_health_bar.blit(self.health_bar.image, (0,0))
        self.health_bar.image = _result_health_bar
        self.health_bar.image.set_alpha(self.image_alpha)
        self.health_bar.draw(surface, vec(0,0))
        
        if self.blit_debug:
            if self.hitbox_body != None:
                self.hitbox_body.draw(surface, offset)
            if self.hitbox_head != None:
                self.hitbox_head.draw(surface, offset)
        
        self.player_offset = offset
        
        
    def get_frames(self, anim_action: enums.AnimActions):
        match anim_action:
            case enums.AnimActions.RUN:
                return self.assets_manager.get_assets(self.enemy_name, "run_frames")
            case enums.AnimActions.ATTACK:
                return self.assets_manager.get_assets(self.enemy_name, "attack_frames")
            case enums.AnimActions.DEATH:
                return self.assets_manager.get_assets(self.enemy_name, "death_frames")
            case enums.AnimActions.BUMP:
                return self.assets_manager.get_assets(self.enemy_name, "bump_frames")
            case _:
                return self.assets_manager.get_assets(self.enemy_name, str(anim_action))
    
    def get_sounds(self, anim_action: enums.AnimActions):
        match anim_action:
            case enums.AnimActions.TAKE_DAMAGE:
                return self.assets_manager.get_assets(self.enemy_name, "damage_sounds")
            case enums.AnimActions.ATTACK:
                return self.assets_manager.get_assets(self.enemy_name, "attack_sounds")
            case enums.AnimActions.DEATH:
                return self.assets_manager.get_assets(self.enemy_name, "death_sounds")
            case enums.AnimActions.BUMP:
                return self.assets_manager.get_assets(self.enemy_name, "bump_sounds")
            case enums.AnimActions.DASH:
                return self.assets_manager.get_assets(self.enemy_name, "dash_sounds")
            case _:
                return self.assets_manager.get_assets(self.enemy_name, str(anim_action))

    def fade_out_anim(self):
        anim_end = (self.death_time + datetime.timedelta(milliseconds=self.fade_out_ms))
        
        self.image_alpha = mc.fade_out_color(colors.WHITE, 255, self.death_time, anim_end)[3]

        if self.image_alpha <= 0:
            self.kill(self.killer)
        
        
    def kill(self, attacker):
        self.wave.handle_score(self, attacker, self.headshot_kill)
        self.wave.enemies_count -= 1
        if self.hitbox_head != None:
            self.hitbox_head.kill()
        if self.hitbox_body != None:
            self.hitbox_body.kill()
        if self.death_callback != None:
            self.death_callback(self)
        super().kill()
        
    
    def collision(self,game, targets: pygame.sprite.Group, direction: enums.Orientation, target = None):
        """Handles collision between the enemy and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the enemy was moving.
        """
        if target == None:
            target = self
        collision_objs = pygame.sprite.spritecollide(target, targets, False)
        if collision_objs:
            game.collision(target, collision_objs, direction)
            return True
        return False
        
        
    def take_damage(self, value: float, attacker = None, head_shot = False):
        # if attacker != None:
            
        if value < 0 or self.dying:
            return
        
        if head_shot:
            value *= self.head_shot_multiplier
            
        self.health_bar.remove_value(value)
        
        self.health = math.clamp(self.health - value, 0, self.health_bar.max_value)
        
        if self.health_bar.target_value <= 0:
            if not self.dying:
                self.killer = attacker
                self.is_alive = False
                self.running = False
                self.attacking = False
                if self.hitbox_head != None:
                    self.hitbox_head.kill()
                if self.hitbox_body != None:
                    self.hitbox_body.kill()
                self.hitbox_head = None
                self.hitbox_body = None
                
            self.dying = True
            self.headshot_kill = head_shot
            
                
        _popup_args = constants.POPUPS["damage"].copy()
        if head_shot:
            _popup_args["text_color"] = colors.YELLOW
            
        mc.popup(Popup(f'-{round(value,2)}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.player_offset, **_popup_args))
        return not self.is_alive


    def get_health(self, value: float):
        if value < 0:
            return
        
        self.health = math.clamp(self.health + value, 0, self.health_bar.max_value)
        
        self.health_bar.add_value(value)
        mc.popup(Popup(f'+{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.player_offset, **constants.POPUPS["health"]))
        
      
    
    def get_netdata(self):
        values = {
            "id": self.id,
            "name": self.name,
            "enemy_name": str(self.enemy_name.name),
            "image_scale": self.image_scale,
            "rect": tuple([*self.rect.topleft, *self.rect.size]),
            "is_alive": self.is_alive,
            
            # ennemy attributes
            "health": self.health,
            "pos": tuple(self.pos),
            "jump_force": self.jump_force,
            "damage": self.damage,
            "movement_speed": self.movement_speed,
            "speed": tuple(self.speed),
            "acceleration": tuple(self.acceleration),
            "dir": tuple(self.dir),

            # animation states
            "running": self.running,
            "attacking": self.attacking,
            "grounded": self.grounded,
            "dying": self.dying
        }
        return values
    
    def load_netdata(self, data: dict):
        self.enemy_name = enums.Enemies[data.pop("enemy_name", str(enums.Enemies.Z_ROGER.name))]
        self.rect = pygame.Rect(data.pop("rect", (0,0, 1,1)))
        self.speed = vec(data.pop("speed", (0,0)))
        self.acceleration = vec(data.pop("acceleration", (0,0)))
        self.dir = vec(data.pop("dir", (0,0)))
        self.pos = vec(data.pop("pos", (0,0)))
        
        
        _health = data.pop("health", 0)
        _health_diff = self.health - _health
        
        if _health_diff > 0:
            self.take_damage(_health_diff)
        elif _health_diff < 0:
            self.get_health(-_health_diff)
        
        #if max health changed
        if _health > self.health_bar.max_value:
            self.health_bar.set_value(_health)
            self.health = _health
        
        for item, value in data.items():
            setattr(self, item, value)
    
    def attack_collision(self, obj):
        _hit_targets = []
        for group in self.attack_targets:
            collisions = pygame.sprite.spritecollide(obj, group, False)
            if collisions:
                _hit_targets.extend([*collisions])
        return _hit_targets