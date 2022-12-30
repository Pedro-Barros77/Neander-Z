import pygame, time
from datetime import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller
from domain.utils import colors, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map
from domain.models.igravitable import IGravitable
from domain.models.rectangle_sprite import Rectangle
from domain.models.ui.pages.page import Page
from domain.models.ui.pages.modals.wave_summary import WaveSummary
from domain.models.ui.pages.modals.pause import Pause
from domain.models.wave_result import WaveResult
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
        
        self.pause_screen: Pause = None
        
        self.wave_summary = None
        
        self.focused = True
        
        
        #ui
        
        self._money_icon = pygame.image.load(f'{constants.IMAGES_PATH}ui\\dollar.png')
        self._ammo_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\pistol_ammo_icon.png'), 3)
        
        
    
    def setup(self):
        """Starts the game.
        """
        
        
        self.map = Map(self.screen, constants.GRAVEYARD_MAP, floor_y = 50)
        self.map.rect.bottomleft = self.screen.get_rect().bottomleft
        game_controller.map_size = vec(self.map.rect.size)
        game_controller.screen_size = vec(self.screen.get_size())
        self.pause_screen = Pause(self)
        
        
        _p1_net_id = int(self.client_type)
        self.player = Player((20, 0), enums.Characters.CARLOS if _p1_net_id != 2 else enums.Characters.CLEITON, net_id = _p1_net_id, name = "P1", screen_size = self.screen.get_size())
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2 = Player((80, 0), enums.Characters.CARLOS if _p1_net_id == 2 else enums.Characters.CLEITON, net_id = 1 if self.client_type == 2 else 2, name = "P2", gravity_enabled = False)
        
        self.collision_group = pygame.sprite.Group([self.map.floor, self.map.left_wall, self.map.right_wall])
        self.players_group =  pygame.sprite.Group([self.player])
        self.jumpable_group = pygame.sprite.Group([self.map.floor])
        self.bullets_group = pygame.sprite.Group()

        self.reset_game()
        
        # exec(recyclables.create_box)
        if self.client_type != enums.ClientType.SINGLE:
            self.jumpable_group.add(self.player2)
            
            
    def new_wave(self, wave):
        self.wave_summary = None
        self.focused = True
        self.current_wave = wave
        
        game_controller.bullet_target_groups.append(self.current_wave.enemies_hitbox_group)
        self.current_wave.start()
            
    def reset_game(self):
        """Resets all players attributes to default values.
        """
        
        self.wave_summary = None
        self.current_wave = Wave_1(self)
        game_controller.screen_size = vec(self.screen.get_size())
        game_controller.map_size = vec(self.map.rect.size)
        game_controller.bullet_target_groups = [self.collision_group, self.current_wave.enemies_hitbox_group]
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
        self.player.backpack.pistol_ammo = 30

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
            self.player2.backpack.pistol_ammo = 30

        
        
        if self.client_type != enums.ClientType.GUEST:
            self.current_wave.start()
            

    def end_wave(self, result: dict[int, WaveResult]):
        _p1 = self.player.net_id if self.player.net_id != 3 else 1
        self.player.money += result[_p1].money

        result[_p1].player = self.player
        
        if self.client_type != enums.ClientType.SINGLE:
            _p2 = self.player2.net_id             
            self.player2.score += result[_p2].score
            self.player2.money += result[_p2].money
            
            result[_p2].player = self.player2
            
        
        
        self.wave_summary = WaveSummary((result[1], result[2] if self.client_type != enums.ClientType.SINGLE else None), start_time = datetime.now())

    
    def draw_ui(self):
        
        _top_margin = 10
        _horizontal_margin = 10
        
        _player_head = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png'), 3)
        _head_rect = _player_head.get_rect()
        _head_rect.top = _top_margin
        _head_rect.left = _horizontal_margin
        
        _health_rect = self.player.health_bar.draw(self.screen, -vec(_head_rect.topright))
        
        _money_icon_rect = self._money_icon.get_rect()
        _money_icon_rect.centery = _head_rect.centery
        _money_icon_rect.left = _health_rect.right + _horizontal_margin

        _txt_money = menu_controller.get_text_surface(f"{self.player.money:.2f}", colors.WHITE, pygame.font.Font(constants.PIXEL_FONT, 25))
        _txt_money_rect = _txt_money.get_rect()
        _txt_money_rect.centery = _head_rect.centery
        _txt_money_rect.left = _money_icon_rect.right + _horizontal_margin

        _txt_score = menu_controller.get_text_surface(f"Score: {self.player.score:.0f}", colors.WHITE, pygame.font.Font(constants.PIXEL_FONT, 25))
        _txt_score_rect = _txt_score.get_rect()
        _txt_score_rect.centery = _head_rect.centery
        _txt_score_rect.left = _txt_money_rect.right + _horizontal_margin*2
        
        _txt_fps = menu_controller.get_text_surface(f'fps: {menu_controller.clock.get_fps():.0f}', colors.LIGHT_GRAY, pygame.font.SysFont('calibri', 20))
        _txt_fps_rect = _txt_fps.get_rect()
        _txt_fps_rect.centery = _head_rect.centery
        _txt_fps_rect.right = self.screen.get_width() - _horizontal_margin
        
        _ammo_icon_rect = self._ammo_icon.get_rect()
        _ammo_icon_rect.bottom = self.screen.get_height() - _top_margin
        _ammo_icon_rect.left = _horizontal_margin
        
        _bullets_color = None
        if self.player.current_weapon.magazine_bullets <= 0:
            _bullets_color = colors.RED
        elif self.player.current_weapon.magazine_bullets >= self.player.current_weapon.magazine_size * 0.3:
            _bullets_color = colors.WHITE
        else:
            _bullets_color = colors.YELLOW
        _txt_ammo = menu_controller.get_text_surface(f'{self.player.current_weapon.magazine_bullets}', _bullets_color, pygame.font.Font(constants.PIXEL_FONT, 20))
        _txt_ammo_rect = _txt_ammo.get_rect()
        _txt_ammo_rect.centery = _ammo_icon_rect.centery
        _txt_ammo_rect.left = _ammo_icon_rect.right + _horizontal_margin
        
        _txt_total_ammo = menu_controller.get_text_surface(f'/ {self.player.backpack.get_ammo(self.player.current_weapon.bullet_type)}', colors.WHITE, pygame.font.Font(constants.PIXEL_FONT, 20))
        _txt_total_ammo_rect = _txt_total_ammo.get_rect()
        _txt_total_ammo_rect.centery = _ammo_icon_rect.centery
        _txt_total_ammo_rect.left = _txt_ammo_rect.right + 2
        
        self.screen.blit(_player_head, _head_rect)
        self.screen.blit(self._money_icon, _money_icon_rect)
        self.screen.blit(_txt_money, _txt_money_rect) 
        self.screen.blit(_txt_score, _txt_score_rect)
        self.screen.blit(_txt_fps, _txt_fps_rect)
        self.screen.blit(self._ammo_icon, _ammo_icon_rect)
        self.screen.blit(_txt_ammo, _txt_ammo_rect)
        self.screen.blit(_txt_total_ammo, _txt_total_ammo_rect)
        
    
            
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
                player_aim_angle = self.player.current_weapon.weapon_aim_angle,
                player_falling_ground = self.player.falling_ground,
                player_running = self.player.running,
                player_jumping = self.player.jumping,
                player_turning_dir = self.player.turning_dir,
                player_firing = self.player.current_weapon.firing
            )
        
        _bullets = [b.get_netdata() for b in self.bullets_group.sprites() if b.owner == self.player.net_id]
        data.bullets = _bullets
        if self.wave_summary != None:
            data.player_wave_ready = self.wave_summary.p1_ready
        
        if self.client_type == enums.ClientType.HOST:
            data.player2_score = self.player2.score
            
            _enemies = [e.get_netdata() for e in self.current_wave.enemies_group.sprites()]
            data.enemies = _enemies
            
            data.wave_results = [] if self.wave_summary == None else [self.wave_summary.P2_RESULT.get_netdata(), self.wave_summary.P1_RESULT.get_netdata()]
        
        return data
    
        
    def handle_received_data(self, data: NetData):
        """Handles the data received from player 2.

        Args:
            data (NetData): An object containing the transfered data.
        """
        if data.command_id == int(enums.Command.RESTART_GAME):
            self.wave_summary = None
            game_controller.restart_game(self)
        
        if self.client_type == enums.ClientType.GUEST:
            self.player.score = data.player2_score
            if len(data.wave_results) > 0 and self.wave_summary == None:
                self.wave_summary = WaveSummary((WaveResult(player = self.player).load_netdata(data.wave_results[0]),WaveResult().load_netdata(data.wave_results[1])))
            
        if self.wave_summary != None:
            self.wave_summary.p2_ready = data.player_wave_ready
        
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
        self.player2.current_weapon.weapon_aim_angle = data.player_aim_angle
        
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
                e = ZRoger((0,0), enums.Enemies.Z_ROGER, self.current_wave)
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

    def send_restart(self):
        self.command_id = int(enums.Command.RESTART_GAME)
            
        time.sleep(0.5)
        game_controller.restart_game(self)
        
        
    def restart_game(self):
        self.focused = True
        self.wave_summary = None
        self.pause_screen.hide()
        if self.client_type == enums.ClientType.SINGLE:
            game_controller.restart_game(self)
        elif self.client_type == enums.ClientType.HOST:
            self.send_restart()

    def update(self, **kwargs):
        events = kwargs.pop("events", None)
        
        game_controller.handle_events(self, events)
        
        if self.wave_summary != None:
            self.focused = False
            self.wave_summary.update(events = events)
            # if wave interval is out or p1 is ready and is singleplayer or both players are ready
            if self.wave_summary.timed_out or (self.wave_summary.p1_ready and (self.wave_summary.p2_ready or self.client_type == enums.ClientType.SINGLE)):
                wave = Wave_1(self)
                self.new_wave(wave)
            return
        
        
        if not pygame.mixer.music.get_busy():
            menu_controller.play_music(constants.get_music(enums.Music.WAVE_1), 0.1, -1)
                
        if pygame.K_l in self.pressed_keys:
            self.restart_game()
        # p1
        self.player.update(game = self)
        # p2
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.update(game = self)
        # wave logic
        self.current_wave.update()
        # enemies
        self.current_wave.update_enemies()
        
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
        if pygame.K_r in self.pressed_keys:
            self.player.reload_weapon()
            self.pressed_keys.remove(pygame.K_r)
        if pygame.K_p in self.pressed_keys:
            self.pause_screen.show()
            self.pressed_keys.remove(pygame.K_p)
        if pygame.K_ESCAPE in self.pressed_keys:
            self.pause_screen.show()
            self.pressed_keys.remove(pygame.K_ESCAPE)
        

        if self.player.pos.y > self.map.rect.height:
            self.player.pos.y = 0
            self.player.update_rect()
            
        if self.client_type != enums.ClientType.SINGLE and self.player2.pos.y > self.map.rect.height:
            self.player2.pos.y = 0
            self.player2.update_rect()
            
        if self.pause_screen != None and self.pause_screen.active:
            if self.player.reload_popup != None:
                self.player.reload_popup.destroy()
                self.player.reload_popup = None
            self.pause_screen.update()
        
    
       
    def draw(self):
        # Map
        self.screen.blit(self.map.image, vec(self.map.rect.topleft) - self.player.offset_camera)
        
        if self.wave_summary != None:
            self.wave_summary.draw(self.screen)
            return
        
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
        
        if self.pause_screen != None and self.pause_screen.active:
            self.pause_screen.draw(self.screen)
        
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
        
        