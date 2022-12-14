import pygame, os
from datetime import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, drawer
from domain.utils import colors, math_utillity as math, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map

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
        
        self.monitor_size = (0,0)
        """The size of the user's monitor.""" 
        
        self.client_type = client_type
        """The type of this client (host or guest)."""
        
        self.gravity_accelaration = 0
        """The acceleration force of the gravity."""
        
        self.friction = 0       
        """The friction between objects."""
        
        self.player_group = None
        """The group of players.""" 
        
        self.collision_group = None
        """The group of objects that should collide.""" 
        
        self.player = None
        """Player 1 (this player).""" 
        
        self.player2 = None
        """Player 2 (other player).""" 
        
        self.map = None
        """The map object for this game level."""
        
        self.command_id = 0
    
    def reset_players(self):
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
        
        self.player2.image = game_controller.scale_image(pygame.image.load(constants.PLAYER_2_IMAGE), 2)
        self.player2.pos = vec(p2_pos)
        self.player2.rect = self.player2.image.get_rect()
        self.player2.rect.topleft = self.player2.pos
        self.player2.size = self.player2.rect.size
        self.player2.speed = vec(0,0)
        self.player2.acceleration = vec(0,0)
        self.player2.last_rect = self.player2.rect
        
    def start(self):
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
        
        self.player = Player((20, 0), constants.PLAYER_1_IMAGE, net_id = self.client_type, name = "P1")
        self.player2 = Player((80, 0), constants.PLAYER_2_IMAGE, net_id = 1 if self.client_type == 2 else 2, name = "P2")
        self.reset_players()
        
        self.player_group = pygame.sprite.Group([self.player, self.player2])
        self.collision_group = pygame.sprite.Group([self.player2, self.map.floor, self.map.left_wall, self.map.right_wall])
        
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
        
        print(data.command_id)
        
        if data.command_id == int(enums.Command.RESTART_GAME):
            print("restarting...")
            game_controller.restart_game(self)
                    
        self.player2.rect.topleft = data.player_pos
        self.player2.pos = vec(data.player_pos)
        self.player2.size = data.player_size
        self.player2.color = data.player_color
        self.player2.speed = vec(data.player_speed)
        self.player2.acceleration = vec(data.player_acceleration)
        self.player2.last_rect = data.player_last_rect
        
        
        self.player2.update_rect()
        
    def in_bounds(self, obj_rect, container_rect, dir: enums.Orientation):
        if dir == enums.Orientation.HORIZONTAL:
            return obj_rect.left > container_rect.left and obj_rect.right < container_rect.width + container_rect.left
        else:
            return obj_rect.top > container_rect.top and obj_rect.bottom < container_rect.height + container_rect.top
        
    def player_movement(self):
        self.player.last_rect = self.player.rect.copy()
        self.player.acceleration = vec(0,self.gravity_accelaration)
        
        if pygame.K_SPACE in self.pressed_keys:
            self.player.speed.y = -self.player.jump_force
            
        if pygame.K_RIGHT in self.pressed_keys and \
           pygame.K_LEFT not in self.pressed_keys:
            
            self.player.acceleration.x = self.gravity_accelaration
            
            _half_screen = self.screen.get_width()/2
            if self.player.pos.x > _half_screen and self.player.pos.x + _half_screen + (-self.map.pos[0]) < self.map.rect.width:
                self.map.rect.left = self.map.pos[0] - self.player.speed.x
                self.map.update_pos()
                self.player.pos.x = _half_screen
        
        if pygame.K_LEFT in self.pressed_keys and \
           pygame.K_RIGHT not in self.pressed_keys:
            self.player.acceleration.x = -self.gravity_accelaration
            
            _half_screen = self.screen.get_width()/2
            if self.player.pos.x < _half_screen and self.map.pos[0] < 0:
                self.map.rect.left = self.map.pos[0] - self.player.speed.x
                self.map.update_pos()
                self.player.pos.x = _half_screen

        if self.player.pos.x > self.screen.get_width():
            self.player.pos.x = 0
        
        if self.player.pos.x < 0:
            self.player.pos.x = self.screen.get_width()

        self.player.acceleration.x += self.player.speed.x * self.friction
        self.player.speed += self.player.acceleration
        self.player.pos += self.player.speed + 0.5 * self.player.acceleration
        
        self.player.update_rect()
        self.handle_player_collision(enums.Orientation.HORIZONTAL)

    def gravity(self):
        pass
        

    def handle_player_collision(self, direction: enums.Orientation):
        """Handles collision between the player and collidable objects.

        Args:
            direction (enums.Orientation): The direction that the player was moving.
        """
        collision_objs = pygame.sprite.spritecollide(self.player, self.collision_group, False)
        if collision_objs:
            self.collision(self.player, collision_objs, direction)
    
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
                    # collision on the right
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

    def game_loop(self):
        while game_controller.playing:
            
            game_controller.handle_events(self)
            
            if pygame.K_r in self.pressed_keys and self.client_type == enums.ClientType.HOST:
                self.command_id = int(enums.Command.RESTART_GAME)
                
                import time
                time.sleep(0.5)
                game_controller.restart_game(self)
            
            self.player_movement()
            self.handle_player_collision(enums.Orientation.VERTICAL)
            
            self.screen.blit(self.map.image, self.map.rect)
            
            
            self.map.floor.image.fill(colors.RED)
            self.map.left_wall.image.fill(colors.RED)
            self.map.right_wall.image.fill(colors.RED)
            self.screen.blit(self.map.floor.image, self.map.floor.rect)
            self.screen.blit(self.map.left_wall.image, self.map.left_wall.rect)
            self.screen.blit(self.map.right_wall.image, self.map.right_wall.rect)
            
            self.player_group.draw(self.screen)
            
            
            pygame.display.update()
            self.clock.tick(60)
        
