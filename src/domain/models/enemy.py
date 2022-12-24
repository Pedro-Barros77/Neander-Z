import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants, math_utillity as math
from domain.services import game_controller, menu_controller
from domain.models.progress_bar import ProgressBar
from domain.models.ui.popup_text import Popup



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_name: enums.Enemies, wave, **kwargs):
        super().__init__()
        
        self.id = kwargs.pop("id", 0)
        self.name = "enemy"
        self.wave = wave
        self.jump_force = 12
        self.damage = 1
        self.enemy_name = enemy_name
        self.image_scale = 2
        self.movement_speed = kwargs.pop("movement_speed", 5)
        self.health = kwargs.pop("health", 30)
        self.attack_targets = game_controller.enemy_target_groups
        self.client_type = enums.ClientType.UNDEFINED
        
        
        
        self.pos: vec = vec((pos))
        self.speed = vec(0,0)
        self.acceleration: vec = vec(0,0)
        self.dir: vec = vec(0,0)
        self.last_dir: vec = self.dir.copy()
        self.grounded = False
        
        self.is_alive = True
        
        self.running = True
        """If the running animation is running."""
        self.run_frame = 0
        """The current frame index of the running animation."""
        run_folder = constants.get_zombie_frames(self.enemy_name, enums.AnimActions.RUN)
        self.run_frames = game_controller.load_sprites(run_folder)
        
        self.attacking = False
        self.attack_frame = 0
        attack_folder = constants.get_zombie_frames(self.enemy_name, enums.AnimActions.ATTACK)
        self.attack_frames = game_controller.load_sprites(attack_folder)
        
        self.image = game_controller.scale_image(self.run_frames[0], self.image_scale)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.image_flip_margin = 10
        self.player_offset = vec(0,0)
        
        #debug
        self.damage_request_count = 0
        self.damage_request_limit = 5
        
        
        self.last_rect = self.rect.copy()
        
        self.health_bar = ProgressBar(self.health, pygame.Rect(self.pos - vec(0,-15), (self.rect.width * 1.3, 7)), 
                border_width = 1, 
                border_color = colors.LIGHT_GRAY, 
                value_anim_speed = 0.2)
        
    def calculate_distance(self, d1: vec, d2: vec):
        distance = d1 - d2
        x, y = abs(distance.x), abs(distance.y)
        return vec(x, y)
    
    def get_closest_player(self, p1, p2):
        if p2 == None:
            return p1
        
        closest = sorted([p1, p2], key= lambda p: self.calculate_distance(vec(p.rect.center), vec(self.rect.center)).x)[0]
        return closest
    
    def client_update(self, **kwargs):
        if not self.is_alive:
            self.kill()
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            
        if self.last_dir.x > self.dir.x:
            flip()
        if self.last_dir.x < self.dir.x:
            flip()
            
        if abs(player_center.x - self.rect.centerx) <= self.attack_distance and player.rect.bottom > self.rect.top:
            self.attacking = True
        
        self.health_bar.update()
            
    def host_update(self, **kwargs):
        if not self.is_alive:
            self.kill()
            
        game = kwargs.pop("game", None)
        player = self.get_closest_player(game.player, game.player2)
        player_center: vec = vec(player.rect.center)
        
        def flip():
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_dir = self.dir.copy()
            self.speed.x = 0
        
        
        if player_center.x < self.rect.centerx - self.image_flip_margin:
            self.dir.x = -1
            if self.last_dir.x > self.dir.x:
                flip()
        elif player_center.x > self.rect.centerx + self.image_flip_margin:
            self.dir.x = 1
            if self.last_dir.x < self.dir.x:
                flip()
        else:
            self.dir.x = 0
            
        self.acceleration.x = 0
        self.last_rect = self.rect.copy()
        
        # Movement
        if self.dir.x != 0:
            self.acceleration.x = self.movement_speed * self.dir.x
        # if not self.attacking:
        #     self.acceleration.x += self.speed.x * game.friction
        #     self.speed.x += self.acceleration.x
        #     self.pos.x += self.speed.x + 0.5 * self.acceleration.x
        
        # Gravity
        game.apply_gravity(self)
        self.update_rect()
        
        # jump
        self.grounded = self.collision(game, game.collision_group, enums.Orientation.VERTICAL)
        # if self.dir.y > 0 and self.grounded:
        #     self.speed.y = - self.jump_force
        
        # solid collision
        self.collision(game, game.collision_group, enums.Orientation.HORIZONTAL)

        if abs(player_center.x - self.rect.centerx) <= self.attack_distance and player.rect.bottom > self.rect.top:
            self.attacking = True

        self.health_bar.update()
    
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
    
    def update(self, **kwargs):
        self.client_type = kwargs.pop("client_type", enums.ClientType.UNDEFINED)
        if self.client_type == enums.ClientType.GUEST:
            self.client_update(**kwargs)
        else:
            self.host_update(**kwargs)
        
        

       
    def draw(self, surface: pygame.Surface, offset: vec):
        self.health_bar.rect.center = vec(self.rect.centerx, self.rect.top - 15) - offset
        surface.blit(self.image, self.pos - offset)
        self.health_bar.draw(surface, vec(0,0))
        self.player_offset = offset

        
    def kill(self, attacker):
        self.wave.handle_score(self.enemy_name, attacker)
        self.wave.enemies_count -= 1
        self.wave.current_wave_step += 1
        super().kill()
        
    
    def collision(self, game, targets: pygame.sprite.Group, direction: enums.Orientation):
        """Handles collision between the enemy and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the enemy was moving.
        """
        collision_objs = pygame.sprite.spritecollide(self, targets, False)
        if collision_objs:
            game.collision(self, collision_objs, direction)
            return True
        return False
        
        
    def take_damage(self, value: float, attacker = None):
        # if attacker != None:
            
        if value < 0:
            return
        self.health_bar.remove_value(value)
        
        self.health = math.clamp(self.health - value, 0, self.health_bar.max_value)
        
        if self.health_bar.target_value <= 0:
            self.is_alive = False
            self.kill(attacker)
        
        menu_controller.popup(Popup(f'-{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.player_offset, **constants.POPUPS["damage"]))
        return not self.is_alive


    def get_health(self, value: float):
        if value < 0:
            return
        
        self.health = math.clamp(self.health + value, 0, self.health_bar.max_value)
        
        self.health_bar.add_value(value)
        menu_controller.popup(Popup(f'+{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.player_offset, **constants.POPUPS["health"]))
        
      
    
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
            "grounded": self.grounded
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
            self.damage_request_count += 1
            if self.damage_request_count > self.damage_request_limit:
                self.take_damage(_health_diff)  
                self.damage_request_count = 0
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