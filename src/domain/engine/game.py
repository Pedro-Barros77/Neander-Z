import pygame, os
from datetime import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, drawer, menu_controller
from domain.engine import enemies_controller
from domain.utils import colors, recyclables, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map
from domain.models.igravitable import IGravitable
from domain.models.rectangle_sprite import Rectangle
from domain.models.ui.pages.page import Page
class Game(Page):
    def __init__(self, client_type: enums.ClientType, screen: pygame.Surface, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        """The game main surface.""" 

        self.drawer = None
        """A service to draw game objects.""" 
        
        self.pressed_keys = []
        
        """A list of the currently pressed keys.""" 
        self.last_pressed_keys = []
        """A list of the pressed keys on the previous frame.""" 
        
        self.monitor_size = (0,0)
        """The size of the user's monitor.""" 
        
        self.client_type = client_type
        """The type of this client (host or guest)."""
        
        self.gravity_accelaration = 0
        """The acceleration force of the gravity."""
        
        self.friction = 0       
        """The friction between objects."""
        
        self.collision_group = None
        """The group of objects that should collide.""" 
        
        self.jumpable_group = None
        """The group of objects the player can jump from.""" 
        
        self.enemies_group = None
        """The group of enemies.""" 
        
        self.player = None
        """Player 1 (this player).""" 
        
        self.player2 = None
        """Player 2 (other player).""" 
        
        self.map = None
        """The map object for this game level."""
        
        self.command_id = 0
        """A command sent from the host to execute some operation on both host and client, such as restart game."""
        
        self.projectiles = []
        """A list of the projectiles that are still in the game screen."""
        
        self.test_objects = []
        
    
    def reset_players(self):
        """Resets all players attributes to default values.
        """        
        game_controller.screen_size = self.screen.get_size()
        game_controller.map_size = vec(self.map.rect.size)
        
        _y = self.screen.get_height() - 200
        
        p1_pos, p2_pos = None, None
        
        if self.client_type == enums.ClientType.HOST:
            p1_pos = (20, _y)
            p2_pos = (80, _y)
        else:
            p1_pos = (80, _y)
            p2_pos = (20, _y)
        
        self.player.image = game_controller.scale_image(pygame.image.load(constants.get_character_frames(self.player.character, enums.AnimActions.IDLE)), self.player.image_scale)
        self.player.rect = self.player.image.get_rect()
        self.player.rect.topleft = vec(p1_pos)
        self.player.speed = vec(0,0)
        self.player.acceleration = vec(0,0)
        self.player.last_rect = self.player.rect
        self.player.offset_camera = vec(0,0)
        
        self.player.load_state(menu_controller.player_state)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.image = game_controller.scale_image(pygame.image.load(constants.get_character_frames(self.player2.character, enums.AnimActions.IDLE)), self.player2.image_scale)
            self.player2.rect = self.player2.image.get_rect()
            self.player2.rect.topleft = vec(p2_pos)
            self.player2.size = self.player2.rect.size
            self.player2.speed = vec(0,0)
            self.player2.acceleration = vec(0,0)
            self.player2.last_rect = self.player2.rect
        
        if self.client_type != enums.ClientType.GUEST:
            enemies_controller.spawn_random_enemy(self)
        
        
        
    def setup(self):
        """Starts the game.
        """        

        game_controller.playing = True
        game_controller.screen_size = vec(self.screen.get_size())
        
        self.drawer = drawer.Drawer(self)

        self.gravity_accelaration = 0.5
        self.friction = -0.12
        
        self.map = Map(self.screen, constants.GRAVEYARD_MAP, floor_y = 50)
        self.map.rect.bottomleft = self.screen.get_rect().bottomleft
        game_controller.map_size = vec(self.map.rect.size)
        
        self.player = Player((20, 0), enums.Characters.CARLOS, net_id = int(self.client_type), name = "P1", screen_size = self.screen.get_size())
        
        
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2 = Player((80, 0), enums.Characters.CLEITON, net_id = 1 if self.client_type == 2 else 2, name = "P2", gravity_enabled = False)
        
        
        
        self.collision_group = pygame.sprite.Group([self.map.floor, self.map.left_wall, self.map.right_wall])
        self.jumpable_group = pygame.sprite.Group([self.map.floor])
        self.enemies_group = pygame.sprite.Group()
        
        self.reset_players()
        
        # exec(recyclables.create_box)
        
        game_controller.bullet_groups = [self.collision_group, self.enemies_group]
        
        
        if self.client_type != enums.ClientType.SINGLE:
            self.collision_group.add(self.player2)
            self.jumpable_group.add(self.player2)
            
    def get_net_data(self):
        data = NetData(
                net_id = self.player.net_id,
                player_rect = (self.player.rect.left, self.player.rect.top, self.player.rect.width, self.player.rect.height),
                player_last_rect = (self.player.last_rect.left, self.player.last_rect.top, self.player.last_rect.width, self.player.last_rect.height),
                player_speed = (self.player.speed.x, self.player.speed.y),
                player_health = self.player.health,
                player_acceleration = (self.player.acceleration.x, self.player.acceleration.y),
                command_id = self.command_id,
                player_mouse_pos = pygame.mouse.get_pos(),
                player_aim_angle = self.player.weapon_aim_angle,
                player_falling_ground = self.player.falling_ground,
                player_running = self.player.running,
                player_jumping = self.player.jumping,
                player_turning_dir = self.player.turning_dir,
                player_firing = self.player.firing,
                
            )
        if self.client_type == enums.ClientType.HOST:
            _enemies = [e.get_netdata() for e in self.enemies_group.sprites()]
            data.enemies = _enemies
            
        return data
        
    def handle_received_data(self, data: NetData):
        """Handles the data received from player 2.

        Args:
            data (NetData): An object containing the transfered data.
        """
        if data.command_id == int(enums.Command.RESTART_GAME):
            game_controller.restart_game(self)
        
        self.player2.rect = pygame.Rect(data.player_rect)
        self.player2.last_rect = pygame.Rect(data.player_last_rect)
        self.player2.speed = vec(data.player_speed)
        _health_diff = self.player2.health - data.player_health
        if _health_diff > 0:
            self.player2.take_damage(_health_diff)
        elif _health_diff < 0:
            self.player2.get_health(-_health_diff)
        
        self.player2.acceleration = vec(data.player_acceleration)
        self.player2.player2_mouse_pos = vec(data.player_mouse_pos)
        self.player.player2_mouse_pos = vec(data.player_mouse_pos)
        self.player2.weapon_aim_angle = data.player_aim_angle
        
        self.player2.falling_ground = data.player_falling_ground
        self.player2.running = data.player_running
        self.player2.jumping = data.player_jumping
        self.player2.turning_dir = data.player_turning_dir
        if data.player_firing:
            self.player2.firing = True
        
        current_enemy_ids = [x.id for x in self.enemies_group.sprites()]
        new_enemy_ids = [x['id'] for x in data.enemies]
        
        if self.client_type == enums.ClientType.GUEST:
            for e_data in data.enemies:
                enemy = [x for x in self.enemies_group.sprites() if x.id == e_data['id']]
                if len(enemy) > 0:
                    enemy[0].load_net_data(e_data)
                else:
                    if len(self.enemies_group.sprites()) < len(data.enemies) and e_data['id'] not in current_enemy_ids:
                        enemies_controller.create_netdata_enemy(self, e_data)
                        
                        
            
        
        self.player.player2_rect = self.player2.rect
        
    def player_movement(self):
        """Handles the movement of player 1.
        """        
        print(self.player.movement_speed)
        self.player.last_rect = self.player.rect.copy()
        self.player.acceleration.x = 0
            
        pressing_right = pygame.K_d in self.pressed_keys
        pressing_left = pygame.K_a in self.pressed_keys
        was_pressing_right = pygame.K_d in self.last_pressed_keys
        was_pressing_left = pygame.K_a in self.last_pressed_keys
            
        # Move right
        if pressing_right:
            # pressing right but not left
            if not pressing_left:
                self.player.acceleration.x = self.player.movement_speed
                # was pressing both left and right, but released left
                if was_pressing_left and was_pressing_right:
                    self.player.running = False
                    self.player.turning_dir = 1
            # started to press right
            if not was_pressing_right:
                self.player.turning_dir = 1
            # started to press left and right
            if pressing_left:
                self.player.running = False
                self.player.turning_dir = -1
        elif was_pressing_right:
                self.player.running = 0
                self.player.turning_dir = -1
            
        # Move left
        if pressing_left:
            # pressing left but not right
            if not pressing_right:
                self.player.acceleration.x = -self.player.movement_speed
                # was pressing both left and right, but released right
                if was_pressing_left and was_pressing_right:
                    self.player.running = False
                    self.player.turning_dir = 1
            # started to press left
            if not was_pressing_left:
                self.player.turning_dir = 1
            # pressing left and right
            if pressing_right:
                self.player.running = False
                self.player.turning_dir = -1
        elif was_pressing_left and not pressing_right:
                self.player.running = 0
                self.player.turning_dir = -1
            
        if pygame.K_UP in self.pressed_keys:
            self.player.get_health(20)
            self.pressed_keys.remove(pygame.K_UP)
            
        if pygame.K_DOWN in self.pressed_keys:
            self.player.take_damage(20)
            self.pressed_keys.remove(pygame.K_DOWN)
            
        # Movement
        self.player.acceleration.x += self.player.speed.x * self.friction
        self.player.speed.x += self.player.acceleration.x
        self.player.rect.left += self.player.speed.x + 0.5 * self.player.acceleration.x
        
        # solid collision
        self.player_collision(self.collision_group, enums.Orientation.HORIZONTAL)
        
        # Gravity
        self.apply_gravity(self.player)
        
        # jump
        _was_grounded = self.player.grounded
        _old_pos = self.player.rect.top
        self.player.grounded = self.player_collision(self.jumpable_group, enums.Orientation.VERTICAL)
        if not _was_grounded and self.player.grounded and abs(_old_pos - self.player.rect.top) > 2 :
            self.player.jumping = False
            self.player.falling_ground = True
            if pressing_left != pressing_right:
                self.player.running = True
        
        if pygame.K_SPACE in self.pressed_keys and self.player.grounded:
            self.player.speed.y = -self.player.jump_force
            if pressing_left != pressing_right:
                self.player.falling_ground = False
                self.player.running = False
                self.player.jumping = True
           
            self.pressed_keys.remove(pygame.K_SPACE)
    
    
    def apply_gravity(self, target: IGravitable):
        """Applies gravity to the specified IGravitable object.

        Args:
            target (IGravitable): The object to apply gravity on.
        """        
        target.last_rect = target.rect.copy()
        
        target.acceleration.y = self.gravity_accelaration
        target.speed.y += target.acceleration.y
        target.rect.top += target.speed.y + 0.5 * target.acceleration.y
    
    def process_gravitables(self):
        """Applies gravity to all gravitable objects (subclasses of IGravitable)"""        
        for obj in IGravitable.instances:
            if obj.gravity_enabled:
                self.apply_gravity(obj)
                obj.rect.top = obj.rect.top
        
            if obj.collision_enabled:
                obstacles = pygame.sprite.spritecollide(obj, self.collision_group, False)
                self.collision(obj, obstacles, enums.Orientation.VERTICAL)
    
    def player_collision(self, targets: pygame.sprite.Group, direction: enums.Orientation):
        """Handles collision between the player and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the player was moving.
        """
        collision_objs = pygame.sprite.spritecollide(self.player, targets, False)
        if collision_objs:
            if direction == enums.Orientation.HORIZONTAL:
                pass
                # print("parede")
            self.collision(self.player, collision_objs, direction)
            return True
        return False
    
    
    def collision(self, obj: pygame.sprite.Sprite, obstacles: list[pygame.sprite.Sprite], direction: enums.Orientation):
        """Calculates the collision between an object and a group of obstacles. Updates the position of the object to prevent overlapping.

        Args:
            obj (pygame.sprite.Sprite): The object to calculate collision.
            obstacles (list[pygame.sprite.Sprite]): A list of obstacles to check collision with obj.
            direction (enums.Orientation): The direction that the obj was moving (vertical or horizontal).
        """   
        
  
        for o in obstacles:
            match direction:
                case enums.Orientation.HORIZONTAL:
                    # collision with obj right and o left
                    if obj.rect.right >= o.rect.left and obj.last_rect.right <= o.last_rect.left:
                        obj.rect.right = o.rect.left
                        obj.speed.x = 0
                        
                    # collision with obj left and o right
                    elif obj.rect.left <= o.rect.right and obj.last_rect.left >= o.last_rect.right:
                        obj.rect.left = o.rect.right
                        obj.speed.x = 0
            
                case enums.Orientation.VERTICAL:
                    # collision on the bottom
                    if obj.rect.bottom >= o.rect.top and obj.last_rect.bottom <= o.last_rect.top:
                        obj.rect.bottom = o.rect.top
                        obj.speed.y = 0
                        
                    # collision on the top
                    elif obj.rect.top >= o.rect.top and obj.last_rect.top >= o.last_rect.bottom:
                        obj.rect.top = o.rect.bottom
                        obj.speed.y = 0

    def center_camera(self):
        """Calculates the required offset from the player to center the camera on.
        """        
        screen_size = self.screen.get_size()
        
        if self.player.rect.left > screen_size[0]/2 and (self.player.rect.left + screen_size[0]/2 < self.map.rect.width) :
            self.player.offset_camera = vec(self.player.rect.left - screen_size[0]/2, 0)#self.player.rect.centery - screen_size[1]/2

    def update(self, **kwargs):
        events = kwargs.pop("events", None)
        
        game_controller.handle_events(self, events)
        
        if pygame.K_r in self.pressed_keys and \
            (self.client_type == enums.ClientType.HOST or self.client_type == enums.ClientType.SINGLE):
            self.command_id = int(enums.Command.RESTART_GAME)
            
            import time
            time.sleep(0.1)
            game_controller.restart_game(self)
            
        self.player.update()
        self.enemies_group.update(group_name = "enemies", game = self, client_type = self.client_type)
        self.collision_group.update(group_name = "collision")
        self.jumpable_group.update(group_name = "jumpable")
    
        self.process_gravitables()    
            
        self.player_movement()
        
        for p in self.projectiles:
            _should_kill = p.move(self.player.offset_camera)
            if _should_kill:
                self.projectiles.remove(p)
        
        self.player_collision(self.collision_group, enums.Orientation.VERTICAL)
        
        self.center_camera()
    
    def draw(self):
        # Map
        self.screen.blit(self.map.image, vec(self.map.rect.topleft) - self.player.offset_camera)
        # self.screen.fill(colors.WHITE)
        # Enemies
        for e in self.enemies_group.sprites():
            e.draw(self.screen, self.player.offset_camera)
        # P1
        self.player.draw(self.screen, self.player.offset_camera)
        # P2
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.draw(self.screen, self.player.offset_camera)
            
        # bullets
        for p in self.projectiles:
            p.draw(self.screen)
        
        self.blit_debug()
        
        self.last_pressed_keys = self.pressed_keys.copy()
        
    def blit_debug(self):
        """Draws objects that are invisible to the player. For debugging only.
        """        
        self.map.floor.image.fill(colors.RED)
        self.map.left_wall.image.fill(colors.RED)
        self.map.right_wall.image.fill(colors.RED)
        self.screen.blit(self.map.floor.image, vec(self.map.floor.rect.topleft) - self.player.offset_camera)
        self.screen.blit(self.map.left_wall.image, vec(self.map.left_wall.rect.topleft) - self.player.offset_camera)
        self.screen.blit(self.map.right_wall.image, vec(self.map.right_wall.rect.topleft) - self.player.offset_camera)
        
        for o in self.test_objects:
            o.draw(self.screen, self.player.offset_camera)
            
        
        