import pygame, os
from datetime import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller
from domain.utils import colors, recyclables, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map
from domain.models.igravitable import IGravitable
from domain.models.rectangle_sprite import Rectangle
from domain.models.ui.pages.page import Page
from domain.content.enemies.z_roger import ZRoger
from domain.content.waves.wave_1 import Wave_1
from domain.content.weapons.small_bullet import SmallBullet

class Game(Page):
    def __init__(self, client_type: enums.ClientType, screen: pygame.Surface, **kwargs):
        super().__init__("Game", **kwargs)
        self.screen = screen
        """The game main surface.""" 
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

        self.players_group = None
        """The group of player that should collide.""" 
        
        self.jumpable_group = None
        """The group of objects the player can jump from.""" 
        
        self.enemies_group = None
        """The group of enemies.""" 
        
        self.bullets_group = None
        """The group of projectiles that are still in the game screen."""
        
        self.player = None
        """Player 1 (this player).""" 
        
        self.player2 = None
        """Player 2 (other player).""" 
        
        self.map = None
        """The map object for this game level."""
        
        self.command_id = 0
        """A command sent from the host to execute some operation on both host and client, such as restart game."""
        
        self.test_objects = []

        self.current_wave = None
    
    def setup(self):
        """Starts the game.
        """
        
        self.map = Map(self.screen, constants.GRAVEYARD_MAP, floor_y = 50)
        self.map.rect.bottomleft = self.screen.get_rect().bottomleft
        game_controller.map_size = vec(self.map.rect.size)
        game_controller.screen_size = vec(self.screen.get_size())
        
        self.player = Player((20, 0), enums.Characters.CARLOS, net_id = int(self.client_type), name = "P1", screen_size = self.screen.get_size())
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2 = Player((80, 0), enums.Characters.CLEITON, net_id = 1 if self.client_type == 2 else 2, name = "P2", gravity_enabled = False)
        
        self.collision_group = pygame.sprite.Group([self.map.floor, self.map.left_wall, self.map.right_wall])
        self.players_group =  pygame.sprite.Group([self.player])
        self.jumpable_group = pygame.sprite.Group([self.map.floor])
        self.bullets_group = pygame.sprite.Group()
        
        self.reset_game()
        
        # exec(recyclables.create_box)
        if self.client_type != enums.ClientType.SINGLE:
            self.jumpable_group.add(self.player2)
            
    def reset_game(self):
        """Resets all players attributes to default values.
        """
        self.current_wave = Wave_1(self)
        game_controller.screen_size = vec(self.screen.get_size())
        game_controller.map_size = vec(self.map.rect.size)
        game_controller.bullet_target_groups = [self.collision_group, self.current_wave.enemies_group]
        game_controller.enemy_target_groups = [self.players_group]
        
        self.gravity_accelaration = 0.5
        self.friction = -0.12
        
        self.bullets_group.empty()
        
        _y = self.screen.get_height() - 200
        
        p1_pos, p2_pos = None, None
        
        if self.client_type == enums.ClientType.HOST:
            p1_pos = (20, _y)
            p2_pos = (80, _y)
        else:
            p1_pos = (80, _y)
            p2_pos = (20, _y)
        
        self.player.image = game_controller.scale_image(pygame.image.load(constants.get_character_frames(self.player.character, enums.AnimActions.IDLE)), self.player.image_scale)
        self.player.pos = vec(p1_pos)
        self.player.rect = self.player.image.get_rect()
        self.player.rect.topleft = self.player.pos
        self.player.speed = vec(0,0)
        self.player.acceleration = vec(0,0)
        self.player.last_rect = self.player.rect
        self.player.offset_camera = vec(0,0)
        self.player.health = self.player.max_health
        self.player.health_bar.value = self.player.max_health
        self.player.health_bar.target_value = self.player.max_health
        self.player.score = 0
        self.player.money = 0

        self.player.load_state(menu_controller.player_state)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.image = game_controller.scale_image(pygame.image.load(constants.get_character_frames(self.player2.character, enums.AnimActions.IDLE)), self.player2.image_scale)
            self.player2.pos = vec(p2_pos)
            self.player2.rect = self.player2.image.get_rect()
            self.player2.rect.topleft = self.player2.pos
            self.player2.size = self.player2.rect.size
            self.player2.speed = vec(0,0)
            self.player2.acceleration = vec(0,0)
            self.player2.last_rect = self.player2.rect
            self.player2.health = self.player2.max_health
            self.player2.health_bar.value = self.player2.max_health
            self.player2.health_bar.target_value = self.player2.max_health
            self.player2.score = 0        
            self.player2.money = 0

        
        
        if self.client_type != enums.ClientType.GUEST:
            self.current_wave.start()

    def end_wave(self, result):
        _p1 = self.player.net_id if self.player.net_id != 3 else 1
        self.player.score += result[_p1].score
        self.player.money += result[_p1].money

        if self.client_type != enums.ClientType.SINGLE:
                
            _p2 = self.player2.net_id             
            self.player2.score += result[_p2].score
            self.player2.money += result[_p2].money

    
    def draw_ui(self):
        _money_logo = pygame.image.load(f'{constants.IMAGES_PATH}ui\\dollar.png')
        _money_logo_rect = pygame.Rect(vec(self.player.health_bar.rect.topright) + vec(10,0), _money_logo.get_size())

        _text_money = menu_controller.get_text_surface(f"{self.player.money:.2f}", colors.WHITE, pygame.font.Font(constants.PIXEL_FONT, 25))
        _text_money_rect = pygame.Rect(vec(_money_logo_rect.topright) + vec(5,0), _text_money.get_size())

        _text_score = menu_controller.get_text_surface(f"Score: {self.player.score:.0f}", colors.WHITE, pygame.font.Font(constants.PIXEL_FONT, 25))

        self.screen.blit(_money_logo, _money_logo_rect)

        self.screen.blit(_text_money, _text_money_rect) 

        self.screen.blit(_text_score, vec(_text_money_rect.topright) + vec(30,0))

        
    
            
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
        
        _bullets = [b.get_netdata() for b in self.bullets_group.sprites() if b.owner == self.player.net_id]
        data.bullets = _bullets
        if self.client_type == enums.ClientType.HOST:
            _enemies = [e.get_netdata() for e in self.current_wave.enemies_group.sprites()]
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
        self.player2.pos = vec(self.player2.rect.topleft)
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
        
        self.player2.update_rect()
        
        current_enemy_ids = [x.id for x in self.current_wave.enemies_group.sprites()]
        if self.client_type == enums.ClientType.GUEST:
            for e_data in data.enemies:
                enemy = [x for x in self.current_wave.enemies_group.sprites() if x.id == e_data['id']]
                if len(enemy) > 0:
                    enemy[0].load_netdata(e_data)
                else:
                    if len(current_enemy_ids) < len(data.enemies) and e_data['id'] not in current_enemy_ids:
                        self.create_netdata_enemy(e_data)

        current_bullets_ids = [x.id for x in self.bullets_group.sprites() if x.owner != self.player.net_id]
        new_bullets_ids = [x['id'] for x in data.bullets]
        
        # kill extra bullets
        if len(current_bullets_ids) > len(data.bullets):
            extra_bullets = [b for b in self.bullets_group.sprites() if b.owner != self.player.net_id and b.id not in new_bullets_ids]
            for b in extra_bullets:
                b.kill()
                
        for b_data in data.bullets:
            # if it's not p1 bullet
            if b_data['owner'] != self.player.net_id:
                # if bullet already exists here, update
                if b_data['id'] in current_bullets_ids:
                    bullet = [b for b in self.bullets_group.sprites() if b.id == b_data['id']]
                    if len(bullet) > 0:
                        bullet[0].load_netdata(b_data)
                else:
                    if len(current_bullets_ids) < len(data.bullets) and b_data['id'] not in current_bullets_ids:
                        self.create_netdata_bullet(b_data)
        
            
        
        self.player.player2_rect = self.player2.rect
    
    def create_netdata_enemy(self, data: dict):
        e = None
        match data["enemy_name"]:
            case str(enums.Enemies.Z_ROGER.name):
                e = ZRoger((0,0), enums.Enemies.Z_ROGER)
                e.load_netdata(data)
                
        
        if e != None:
            self.current_wave.spawn_enemy(e)
    
    def create_netdata_bullet(game, data: dict):
        b = None
        match data["bullet_name"]:
            case str(enums.Bullets.SMALL_BULLET.name):
                b = SmallBullet(vec(0,0), 0, 0, 0, '', 0)
                b.load_netdata(data)
        
        if b != None:
            game.bullets_group.add(b)
            
    
    
    
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

        if self.client_type != enums.ClientType.SINGLE:
            self.player2.player2_offset = self.player.offset_camera

    def update(self, **kwargs):
        events = kwargs.pop("events", None)
        
        game_controller.handle_events(self, events)
        
        if pygame.K_r in self.pressed_keys and \
            (self.client_type == enums.ClientType.HOST or self.client_type == enums.ClientType.SINGLE):
            self.command_id = int(enums.Command.RESTART_GAME)
            
            import time
            time.sleep(0.1)
            game_controller.restart_game(self)
            
        self.player.update(game = self)
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.update(game = self)
        self.current_wave.update()
        self.collision_group.update(group_name = "collision")
        self.jumpable_group.update(group_name = "jumpable")
    
        self.process_gravitables()    
            
        
        self.bullets_group.update(offset = self.player.offset_camera)
        
        self.center_camera()
        
        #debug
        if pygame.K_UP in self.pressed_keys:
            self.player.get_health(20)
            self.pressed_keys.remove(pygame.K_UP)
        if pygame.K_DOWN in self.pressed_keys:
            self.player.take_damage(20)
            self.pressed_keys.remove(pygame.K_DOWN)
        if pygame.K_DELETE in self.pressed_keys:
            self.current_wave.kill_all()
            self.pressed_keys.remove(pygame.K_DELETE)
    
       
    def draw(self):
        # Map
        self.screen.blit(self.map.image, vec(self.map.rect.topleft) - self.player.offset_camera)
        # Wave
        self.current_wave.draw(self.screen, self.player.offset_camera)
        # P1
        self.player.draw(self.screen, self.player.offset_camera)
        # P2
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.draw(self.screen, self.player.offset_camera)
            
        # bullets
        for b in self.bullets_group:
            b.draw(self.screen, self.player.offset_camera)
        
        # self.blit_debug()
        
        self.last_pressed_keys = self.pressed_keys.copy()

        self.draw_ui()
        
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
        
        for e in self.current_wave.enemies_group.sprites():
            if e.hit_rectangle != None:
                e.hit_rectangle.draw(self.screen, self.player.offset_camera)
        
        