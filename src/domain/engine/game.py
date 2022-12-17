import pygame, os
from datetime import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, drawer
from domain.engine import enemies_controller
from domain.utils import colors, math_utillity as math, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map
from domain.models.igravitable import IGravitable
from domain.models.enemies.zombie_1 import Zombie1
from domain.models.weapon import Weapon
class Game:
    def __init__(self, client_type: enums.ClientType):
        self.screen = None
        """The game main surface.""" 
               
        self.clock = None
        """Pygame clock to control FPS.""" 
        
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
        
    
    def reset_players(self):
        """Resets all players attributes to default values.
        """        
        _y = self.screen.get_height() - 200
        
        p1_pos, p2_pos = None, None
        
        if self.client_type == enums.ClientType.HOST:
            p1_pos = (20, _y)
            p2_pos = (80, _y)
        else:
            p1_pos = (80, _y)
            p2_pos = (20, _y)
        
        self.player.image = game_controller.scale_image(pygame.image.load(constants.PLAYER_1_IMAGE), 2)
        self.player.pos = vec(p1_pos)
        self.player.rect = self.player.image.get_rect()
        self.player.rect.topleft = self.player.pos
        self.player.size = self.player.rect.size
        self.player.speed = vec(0,0)
        self.player.acceleration = vec(0,0)
        self.player.last_rect = self.player.rect
        self.player.offset_camera = vec(0,0)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.image = game_controller.scale_image(pygame.image.load(constants.PLAYER_2_IMAGE), 2)
            self.player2.pos = vec(p2_pos)
            self.player2.rect = self.player2.image.get_rect()
            self.player2.rect.topleft = self.player2.pos
            self.player2.size = self.player2.rect.size
            self.player2.speed = vec(0,0)
            self.player2.acceleration = vec(0,0)
            self.player2.last_rect = self.player2.rect
        
        
    def start(self):
        """Starts the game.
        """        
        pygame.init()
        
        if self.monitor_size == (0,0):
            self.monitor_size = (900, 600)
            
        self.screen = pygame.display.set_mode(self.monitor_size)

        game_controller.playing = True
        
        self.clock = pygame.time.Clock()
        self.drawer = drawer.Drawer(self)

        self.gravity_accelaration = 0.5
        self.friction = -0.12
        
        self.map = Map(self.screen, constants.GRAVEYARD_MAP, floor_y = 50)
        self.map.rect.bottomleft = self.screen.get_rect().bottomleft
        
        self.player = Player((20, 0), constants.PLAYER_1_IMAGE, net_id = int(self.client_type), name = "P1")
        self.player.health_bar.set_width(self.screen.get_width()/2)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2 = Player((80, 0), constants.PLAYER_2_IMAGE, net_id = 1 if self.client_type == 2 else 2, name = "P2", gravity_enabled = False)
        
        
        self.reset_players()
        
        self.collision_group = pygame.sprite.Group([self.map.floor, self.map.left_wall, self.map.right_wall])
        self.jumpable_group = pygame.sprite.Group([self.map.floor])
        self.enemies_group = pygame.sprite.Group()
        
        # enemies_controller.spawn_random_enemy(self)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.collision_group.add(self.player2)
            self.jumpable_group.add(self.player2)
        
        if self.client_type == enums.ClientType.HOST:
            game_controller.host_game(self, constants.SERVER_ADDRESS, constants.SERVER_PORT)
            
        elif self.client_type == enums.ClientType.GUEST:
            game_controller.enter_game(self, constants.SERVER_ADDRESS, constants.SERVER_PORT)
        
        self.game_loop()
        
    def handle_received_data(self, data: NetData):
        """Handles the data received from player 2.

        Args:
            data (NetData): An object containing the transfered data.
        """        
        
        if data.command_id == int(enums.Command.RESTART_GAME):
            game_controller.restart_game(self)
                    
        self.player2.rect.topleft = data.player_pos
        self.player2.pos = vec(data.player_pos)
        self.player2.size = data.player_size
        self.player2.speed = vec(data.player_speed)
        self.player2.acceleration = vec(data.player_acceleration)
        self.player2.last_rect = data.player_last_rect
        self.player2.player2_mouse_pos = vec(data.player2_mouse_pos)
        self.player2.player2_offset_camera = vec(data.player2_offset_camera)
        self.player2.weapon_container_angle = data.player2_aim_angle
        self.player2.update_rect()
        
    def player_movement(self):
        """Handles the movement of player 1.
        """        
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
                self.player.acceleration.x = self.gravity_accelaration
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
                self.player.acceleration.x = -self.gravity_accelaration
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
            self.enemies_group.sprites()[0].get_health(5)
            self.pressed_keys.remove(pygame.K_UP)
            
        if pygame.K_DOWN in self.pressed_keys:
            self.player.take_damage(20)
            self.enemies_group.sprites()[0].take_damage(5)
            self.pressed_keys.remove(pygame.K_DOWN)
            
        # Movement
        self.player.acceleration.x += self.player.speed.x * self.friction
        self.player.speed.x += self.player.acceleration.x
        self.player.pos.x += self.player.speed.x + 0.5 * self.player.acceleration.x
        
        # Gravity
        self.apply_gravity(self.player)
        self.player.update_rect()
        
        # jump
        _was_grounded = self.player.grounded
        _old_pos = self.player.pos.y
        self.player.grounded = self.player_collision(self.jumpable_group, enums.Orientation.VERTICAL)
        if not _was_grounded and self.player.grounded and abs(_old_pos - self.player.pos.y) > 2 :
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
        
        # solid collision
        self.player_collision(self.collision_group, enums.Orientation.HORIZONTAL)
    
    
    def apply_gravity(self, target: IGravitable):
        """Applies gravity to the specified IGravitable object.

        Args:
            target (IGravitable): The object to apply gravity on.
        """        
        target.last_rect = target.rect.copy()
        
        target.acceleration.y = self.gravity_accelaration
        target.speed.y += target.acceleration.y
        target.pos.y += target.speed.y + 0.5 * target.acceleration.y
    
    def process_gravitables(self):
        """Applies gravity to all gravitable objects (subclasses of IGravitable)"""        
        for obj in IGravitable.instances:
            if obj.gravity_enabled:
                self.apply_gravity(obj)
                obj.rect.top = obj.pos.y
        
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
                        obj.pos.x = obj.rect[0]
                        obj.speed.x = 0
                        
                    # collision on the left
                    elif obj.rect.left <= o.rect.right and obj.last_rect.left >= o.last_rect.right:
                        obj.rect.left = o.rect.right
                        obj.pos.x = obj.rect[0]
                        obj.speed.x = 0
            
                case enums.Orientation.VERTICAL:
                    # collision on the bottom
                    if obj.rect.bottom >= o.rect.top and obj.last_rect.bottom <= o.last_rect.top:
                        obj.rect.bottom = o.rect.top
                        obj.pos.y = obj.rect[1]
                        obj.speed.y = 0
                        
                    # collision on the top
                    elif obj.rect.top >= o.rect.top and obj.last_rect.top >= o.last_rect.bottom:
                        obj.rect.top = o.rect.bottom
                        obj.pos.y = obj.rect[1]
                        obj.speed.y = 0

    def center_camera(self):
        """Calculates the required offset from the player to center the camera on.
        """        
        screen_size = self.screen.get_size()
        
        if self.player.pos.x > screen_size[0]/2 and (self.player.pos.x + screen_size[0]/2 < self.map.rect.width) :
            self.player.offset_camera = vec(self.player.rect.left - screen_size[0]/2, 0)#self.player.rect.centery - screen_size[1]/2

    def game_loop(self):
        """Main game loop.
        """        
        
        while game_controller.playing:
            
            game_controller.handle_events(self)
            
            if pygame.K_r in self.pressed_keys and \
                (self.client_type == enums.ClientType.HOST or self.client_type == enums.ClientType.SINGLE):
                self.command_id = int(enums.Command.RESTART_GAME)
                
                import time
                time.sleep(0.1)
                game_controller.restart_game(self)
                
            self.player.update()
            self.enemies_group.update()
            self.collision_group.update()
            self.jumpable_group.update()
        
            self.process_gravitables()    
                
            self.player_movement()
            enemies_controller.enemies_movement(self, self.enemies_group)
            
            self.player_collision(self.collision_group, enums.Orientation.VERTICAL)
            
            self.center_camera()
            
            # Map
            self.screen.blit(self.map.image, vec(self.map.rect.topleft) - self.player.offset_camera)
            # self.screen.fill(colors.WHITE)
            # Enemies
            self.drawer.draw_enemies(self.screen, self.enemies_group)
            # P1
            self.player.draw(self.screen, self.player.offset_camera)
            # P2
            if self.client_type != enums.ClientType.SINGLE:
                self.player2.draw(self.screen, self.player.offset_camera)
            
            # self.blit_debug()
            
            self.last_pressed_keys = self.pressed_keys.copy()
            
            pygame.display.update()
            self.clock.tick(60)
        
    def blit_debug(self):
        """Draws objects that are invisible to the player. For debugging only.
        """        
        self.map.floor.image.fill(colors.RED)
        self.map.left_wall.image.fill(colors.RED)
        self.map.right_wall.image.fill(colors.RED)
        self.screen.blit(self.map.floor.image, self.map.floor.pos - self.player.offset_camera)
        self.screen.blit(self.map.left_wall.image, self.map.left_wall.pos - self.player.offset_camera)
        self.screen.blit(self.map.right_wall.image, self.map.right_wall.pos - self.player.offset_camera)
        