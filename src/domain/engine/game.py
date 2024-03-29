import pygame, time
import datetime
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller as mc, resources
from domain.utils import colors, enums, constants
from domain.utils.math_utillity import sum_tuple_infix as t
from domain.models.player import Player
from domain.models.network_data import Data as NetData
from domain.models.map import Map
from domain.models.igravitable import IGravitable
from domain.models.rectangle_sprite import Rectangle
from domain.models.ui.pages.page import Page
from domain.models.ui.pages.modals.wave_summary import WaveSummary
from domain.models.wave import Wave
from domain.models.ui.pages.modals.pause import Pause
from domain.models.ui.popup_text import Popup
from domain.models.wave_result import WaveResult
from domain.content.enemies.z_roger import ZRoger
from domain.content.waves.simple_wave import SimpleWave
from domain.content.waves.boss_wave import BossWave
from domain.content.weapons.projectile import Projectile
from domain.content.weapons.charge import Charge

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

        self.current_wave: Wave = None
        
        self.pause_screen: Pause = None
        
        self.wave_summary = None
        
        self.focused = True
        
        self.game_over_time: datetime.datetime = None
        self.game_over_popup: Popup = None
        
        #ui
        
        self._money_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\dollar.png').convert_alpha()
        self._pistol_ammo_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\pistol_ammo_icon.png'), 3, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self._shotgun_ammo_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\shotgun_ammo_icon.png'), 2.7, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self._rifle_ammo_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\rifle_ammo_icon.png'), 2.8, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self._sniper_ammo_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\sniper_ammo_icon.png'), 2.5, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self._rocket_ammo_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\rocket_ammo_icon.png'), 2.4, convert_type=enums.ConvertType.CONVERT_ALPHA)

        self._frag_grenade_icon = game_controller.scale_image(pygame.image.load(resources.get_weapon_path(enums.Throwables.FRAG_GRENADE, enums.AnimActions.ICON)), 1.5, convert_type=enums.ConvertType.CONVERT_ALPHA)
        self._molotov_icon = game_controller.scale_image(pygame.image.load(resources.get_weapon_path(enums.Throwables.MOLOTOV, enums.AnimActions.ICON)), 0.6, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        
        
    def setup(self):
        """Starts the game.
        """
        
        self.current_wave = self.create_wave(constants.WAVES[1])
        self.start_wave()
        self.map = Map(self.screen, f"{resources.IMAGES_PATH}map_graveyard.png", floor_y = 50)
        self.map.rect.bottomleft = self.screen.get_rect().bottomleft
        game_controller.map_size = vec(self.map.rect.size)
        game_controller.screen_size = vec(self.screen.get_size())
        game_controller.screen_size = vec(self.screen.get_size())
        game_controller.map_size = vec(self.map.rect.size)
        self.pause_screen = Pause(self)
        self.gravity_accelaration = 0.5
        self.friction = -0.12
        
        _p1_net_id = int(self.client_type)
        self.player = Player((500, 0), enums.Characters.CARLOS if _p1_net_id != 2 else enums.Characters.CLEITON, net_id = _p1_net_id, name = "P1", screen_size = self.screen.get_size())
        self.player.load_state(mc.player_state)
        self.player.rect.bottom = self.map.floor.rect.top
        self.player.pos = vec(self.player.rect.topleft)
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2 = Player((80, 0), enums.Characters.CARLOS if _p1_net_id == 2 else enums.Characters.CLEITON, net_id = 1 if self.client_type == 2 else 2, name = "P2", gravity_enabled = False)
            self.player2.rect.bottom = self.map.floor.rect.top
            self.player2.pos = vec(self.player.rect.topleft)
        
        self.collision_group = pygame.sprite.Group([self.map.floor, self.map.left_wall, self.map.right_wall])
        self.players_group =  pygame.sprite.Group([self.player.hitbox_body])
        self.jumpable_group = pygame.sprite.Group([self.map.floor])
        self.bullets_group = pygame.sprite.Group()

        game_controller.bullet_target_groups = [self.collision_group, self.current_wave.enemies_hitbox_group]
        game_controller.enemy_target_groups = [self.players_group]
        game_controller.collision_group = self.collision_group
        
        
        if self.client_type != enums.ClientType.SINGLE:
            self.jumpable_group.add(self.player2)
            
        
    
    def next_wave(self):
        next_wave = 0 
        if self.current_wave == None:
            next_wave = 1
        elif len(constants.WAVES) < self.current_wave.wave_number+1:
            next_wave = 1
        else:
            next_wave = self.current_wave.wave_number+1
        
        self.current_wave = self.create_wave(constants.WAVES[next_wave])
        self.start_wave()
    
    def create_wave(self, values_dict: dict):
        dic = values_dict.copy()
        match values_dict["wave_type"]:
            case enums.WaveType.SIMPLE:
                return SimpleWave(self, **dic)
            case enums.WaveType.BOSS:
                return BossWave(self, **dic)
            
    def start_wave(self):
        self.pressed_keys.clear()
        self.wave_summary = None
        self.focused = True
        
        game_controller.bullet_target_groups.append(self.current_wave.enemies_hitbox_group)

        if self.game_over_popup != None:
            self.game_over_popup.destroy()
        self.current_wave.start()


            

    def end_wave(self, result: dict[int, WaveResult]):
        _p1 = self.player.net_id if self.player.net_id != 3 else 1
        self.player.money += result[_p1].money

        result[_p1].player = self.player
        
        self.player.survived_wave += 1
        
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.survived_wave += 1
            _p2 = self.player2.net_id             
            self.player2.score += result[_p2].score
            self.player2.money += result[_p2].money
            
            result[_p2].player = self.player2
            
        
        
        self.wave_summary = WaveSummary((result[1], result[2] if self.client_type != enums.ClientType.SINGLE else None), start_time = datetime.datetime.now())

    def get_ammo_icon(self, bullet_type: enums.BulletType):
        match bullet_type:
            case enums.BulletType.PISTOL:
                return self._pistol_ammo_icon
            case enums.BulletType.SHOTGUN:
                return self._shotgun_ammo_icon
            case enums.BulletType.ASSAULT_RIFLE:
                return self._rifle_ammo_icon
            case enums.BulletType.SNIPER:
                return self._sniper_ammo_icon
            case enums.BulletType.ROCKET:
                return self._rocket_ammo_icon
            case enums.BulletType.MELEE:
                return None
            
            case enums.Throwables.FRAG_GRENADE:
                return self._frag_grenade_icon
            case enums.Throwables.MOLOTOV:
                return self._molotov_icon
    
    def draw_ui(self):
        
        _top_margin = 10
        _horizontal_margin = 10
        bkp = self.player.backpack
        
        _player_head = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png'), 3, convert_type=enums.ConvertType.CONVERT_ALPHA)
        _head_rect = _player_head.get_rect()
        _head_rect.top = _top_margin
        _head_rect.left = _horizontal_margin
        
        _health_rect = self.player.health_bar.draw(self.screen, -vec(_head_rect.topright))
        
        _money_icon_rect = self._money_icon.get_rect()
        _money_icon_rect.centery = _head_rect.centery
        _money_icon_rect.left = _health_rect.right + _horizontal_margin

        _txt_money = mc.get_text_surface(f"{self.player.money:.2f}", colors.WHITE, resources.px_font(25))
        _txt_money_rect = _txt_money.get_rect()
        _txt_money_rect.centery = _head_rect.centery
        _txt_money_rect.left = _money_icon_rect.right + _horizontal_margin

        _txt_score = mc.get_text_surface(f"Score: {self.player.score:.0f}", colors.WHITE, resources.px_font(25))
        _txt_score_rect = _txt_score.get_rect()
        _txt_score_rect.centery = _head_rect.centery
        _txt_score_rect.left = _txt_money_rect.right + _horizontal_margin*2
        
        
        _txt_wave_number = mc.get_text_surface(f"Wave {self.current_wave.wave_number}", colors.PASTEL_RED, resources.px_font(18))
        _txt_wave_number_rect = _txt_wave_number.get_rect()
        _txt_wave_number_rect.top = _txt_score_rect.bottom + _top_margin
        _txt_wave_number_rect.right = self.screen.get_width() - _horizontal_margin
        
        
        _skull = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\skull.png'), 0.8, convert_type=enums.ConvertType.CONVERT_ALPHA)
        _skull_rect = _skull.get_rect()
        _skull_rect.top = _txt_wave_number_rect.bottom + _top_margin/2
        _skull_rect.right = self.screen.get_width() - _horizontal_margin
        
        _has_boss = type(self.current_wave) == BossWave and (self.current_wave.boss == None or self.current_wave.boss.is_alive)
        _txt_enemies_count = mc.get_text_surface(f"{self.current_wave.killed_enemies_count}/{'-' if _has_boss else self.current_wave.total_enemies}", colors.LIGHT_GRAY, resources.px_font(18))
        _txt_enemies_rect = _txt_enemies_count.get_rect()
        _txt_enemies_rect.centery = _skull_rect.centery
        _txt_enemies_rect.right = _skull_rect.left - _horizontal_margin
        
        
        _weapon_size = 40
        _sec_weapon_size = 20
        _weapon_offset = 0
        
        _weapon_icon = None
        _equiped_prim = False
        
        #primary
        if bkp.equipped_primary != None and self.player.current_weapon.weapon_type == bkp.equipped_primary:
            _weapon_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_primary, enums.AnimActions.ICON))
            _equiped_prim = True
            
        elif bkp.equipped_secondary != None and self.player.current_weapon.weapon_type == bkp.equipped_secondary:
            _weapon_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_secondary, enums.AnimActions.ICON))

        _max_dim = max(*_weapon_icon.get_size())
        _ratio = abs(_weapon_icon.get_width() / _weapon_icon.get_height())
        if _ratio >= 4:
            _max_dim *= 0.8
            
        _percentage = ((_weapon_size * 100 / _max_dim)/100)
        _weapon_icon = game_controller.scale_image(_weapon_icon, _percentage, enums.ConvertType.CONVERT_ALPHA)
        _weapon_icon_rect = _weapon_icon.get_rect()
        _weapon_icon_rect.left = _horizontal_margin
        if _weapon_icon_rect.width < _weapon_size:
            _weapon_offset = _weapon_size
            
        ##
        
        
        #secondary
        _sec_weapon_icon = None
        if bkp.equipped_secondary != None and bkp.equipped_primary != None:
            if _equiped_prim:
                _sec_weapon_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_secondary, enums.AnimActions.ICON))
            else:
                _sec_weapon_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_primary, enums.AnimActions.ICON))
        if _sec_weapon_icon != None:
            _max_dim = max(*_sec_weapon_icon.get_size())
            _ratio = abs(_sec_weapon_icon.get_width() / _sec_weapon_icon.get_height())
            if _ratio >= 4:
                _max_dim *= 0.6
                
            _percentage = ((_sec_weapon_size * 100 / _max_dim)/100)
            _sec_weapon_icon = game_controller.scale_image(_sec_weapon_icon, _percentage, enums.ConvertType.CONVERT_ALPHA)
            _sec_weapon_icon_rect = _sec_weapon_icon.get_rect()
            _sec_weapon_icon_rect.left = _weapon_icon_rect.right + _weapon_offset
        ##
        
        #ammo
        if self.player.current_weapon.bullet_type != enums.BulletType.MELEE:
            _ammo_icon = self.get_ammo_icon(self.player.current_weapon.bullet_type)
            _ammo_icon_rect = _ammo_icon.get_rect()
            _ammo_icon_rect.bottom = self.screen.get_height() - _top_margin
            _ammo_icon_rect.left = max(_weapon_icon_rect.right + _horizontal_margin, _weapon_offset)
            ##
            _weapon_icon_rect.centery = _ammo_icon_rect.centery
        else:
            _weapon_icon_rect.bottom = self.screen.get_height() - _top_margin
        
        #swap
        if _sec_weapon_icon != None:
            _sec_weapon_icon_rect.bottom = _weapon_icon_rect.top - _top_margin
            _swap_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\swap.png'), 0.8, convert_type=enums.ConvertType.CONVERT_ALPHA)
            _swap_icon_rect = _swap_icon.get_rect()
            _swap_icon_rect.centery = _sec_weapon_icon_rect.centery
            _swap_icon_rect.centerx = max(_weapon_icon_rect.centerx, _weapon_offset)
        ##
        
        ##ammo
        _bullets_color = None
        if self.player.current_weapon.magazine_bullets <= 0:
            _bullets_color = colors.RED
        elif self.player.current_weapon.magazine_bullets >= self.player.current_weapon.magazine_size * 0.3:
            _bullets_color = colors.WHITE
        else:
            _bullets_color = colors.YELLOW
        
        if self.player.current_weapon.bullet_type != enums.BulletType.MELEE:
            _txt_ammo = mc.get_text_surface(f'{self.player.current_weapon.magazine_bullets}', _bullets_color, resources.px_font(20))
            _txt_total_ammo = mc.get_text_surface(f'/ {bkp.get_ammo(self.player.current_weapon.bullet_type)}', colors.WHITE, resources.px_font(20))
        else:
            _txt_ammo = mc.get_text_surface('-', colors.WHITE, resources.px_font(20))
            _txt_total_ammo = mc.get_text_surface(f'/-', colors.WHITE, resources.px_font(20))
            
        _txt_ammo_rect = _txt_ammo.get_rect()
        _txt_ammo_rect.centery = _weapon_icon_rect.centery
        if self.player.current_weapon.bullet_type != enums.BulletType.MELEE:
            _txt_ammo_rect.left = _ammo_icon_rect.right + _horizontal_margin
        else:
            _txt_ammo_rect.left = _weapon_icon_rect.right + _horizontal_margin
        
        _txt_total_ammo_rect = _txt_total_ammo.get_rect()
        _txt_total_ammo_rect.centery = _txt_ammo_rect.centery
        _txt_total_ammo_rect.left = _txt_ammo_rect.right + 2
        ##
        
        #grenade
        _throwable_icon = self.get_ammo_icon(self.player.current_throwable.weapon_type)
        _throwable_icon_rect = _throwable_icon.get_rect()
        _throwable_icon_rect.centery = _weapon_icon_rect.centery
        _throwable_icon_rect.left = _txt_total_ammo_rect.right + _horizontal_margin*3
        
        _throwable_color = colors.WHITE if self.player.current_throwable.count > 0 else colors.RED
        _txt_throwables = mc.get_text_surface(f'{self.player.current_throwable.count}', _throwable_color, resources.px_font(16))
        _txt_throwables_rect = _txt_throwables.get_rect()
        _txt_throwables_rect.centery = _throwable_icon_rect.centery
        _txt_throwables_rect.left = _throwable_icon_rect.right + _horizontal_margin
        
        ##
        
        
        
        self.screen.blit(_player_head, _head_rect)
        self.screen.blit(self._money_icon, _money_icon_rect)
        self.screen.blit(_txt_money, _txt_money_rect) 
        self.screen.blit(_txt_score, _txt_score_rect)
        _enemies_bg = pygame.Rect((_txt_enemies_rect.left, _txt_wave_number_rect.top) - vec(5,2), vec(_txt_enemies_rect.width, _txt_enemies_rect.height + _txt_wave_number_rect.height + _top_margin) + vec(self.screen.get_width() - _skull_rect.right + _skull_rect.width + _horizontal_margin, 0) + vec(10,3))
        pygame.draw.rect(self.screen, colors.MEDIUM_GRAY, _enemies_bg)
        self.screen.blit(_txt_wave_number, _txt_wave_number_rect)
        self.screen.blit(_skull, _skull_rect)
        self.screen.blit(_txt_enemies_count, _txt_enemies_rect)
        
        self.screen.blit(_weapon_icon, _weapon_icon_rect)
        if _sec_weapon_icon != None:
            self.screen.blit(_sec_weapon_icon, _sec_weapon_icon_rect)
            self.screen.blit(_swap_icon, _swap_icon_rect)
        if self.player.current_weapon.bullet_type != enums.BulletType.MELEE:
            self.screen.blit(_ammo_icon, _ammo_icon_rect)
        self.screen.blit(_txt_ammo, _txt_ammo_rect)
        self.screen.blit(_txt_total_ammo, _txt_total_ammo_rect)
        self.screen.blit(_throwable_icon, _throwable_icon_rect)
        self.screen.blit(_txt_throwables, _txt_throwables_rect)
        
    
            
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
                player_jumping = self.player.jumping_sideways,
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
            self.restart_game()
        
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
        self.player2.jumping_sideways = data.player_jumping
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
                e = ZRoger((0,0), self.current_wave)
                e.load_netdata(data)
                
        
        if e != None:
            self.current_wave.spawn_enemy(e)
    
    def create_netdata_bullet(game, data: dict):
        b = None
        match data["bullet_type"]:
            case str(enums.BulletType.PISTOL.name):
                b = Projectile(vec(0,0), 0, 0, 0, '', 0)
                b.load_netdata(data)
        
        if b != None:
            game.bullets_group.add(b)
            
    def apply_gravity(self, target: IGravitable):
        """Applies gravity to the specified IGravitable object.

        Args:
            target (IGravitable): The object to apply gravity on.
        """        
        target.last_rect = target.rect.copy()
        
        _scale = target.gravity_scale if hasattr(target, "gravity_scale") else 1
        target.acceleration.y = self.gravity_accelaration
        target.speed.y += target.acceleration.y * mc.dt * _scale
        target.pos.y += (target.speed.y + 0.5 * target.acceleration.y) * mc.dt
    
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
        self.restart_game()
        
        
    def restart_game(self):
        if self.game_over_popup != None:
            self.game_over_popup.destroy()
        game_controller.restart_game(self)

    def game_over(self):
        self.game_over_time = datetime.datetime.now()
        self.focused = False
        pygame.mouse.set_cursor()
        self.game_over_popup = Popup("Game Over", (0,0), show_on_init = False, **constants.POPUPS["game_over"])
        mc.popup(self.game_over_popup, center=True)
        self.game_over_popup.rect.top -= self.game_over_popup.rect.height
        self.pause_screen.title = ""
        self.pause_screen.buttons[0].visible = False
            
    def handle_shooting(self):
        #if current weapon has burst firemode and can shoot one more round
        _is_burst = self.player.current_weapon.fire_mode == enums.FireMode.BURST
        
        if self.player.rolling or self.player.current_throwable.throwing or self.player.current_throwable.cook_start_time != None:
            return
        
        if "mouse_0" not in self.pressed_keys and (not _is_burst or(_is_burst and not self.player.current_weapon.firing_burst)):
            return
        
        if self.player.current_weapon.reload_type == enums.ReloadType.SINGLE_BULLET and self.player.current_weapon.bullet_type == enums.BulletType.SHOTGUN:
            self.player.current_weapon.reloading = False
        
        def bullet_kill_callback(hit_target):
            if hit_target:
                self.current_wave.players_scores[1].bullets_hit += 1
        
        
        _bullets = self.player.shoot(kill_callback = bullet_kill_callback)
        
        #if current weapon doesn't allow holding trigger
        if self.player.current_weapon.fire_mode not in constants.HOLD_TRIGGER_FIREMODES:
            if "mouse_0" in self.pressed_keys:
                self.pressed_keys.remove("mouse_0")
        
        if _bullets == None:
            return
        

        if type(_bullets) != list:
            _bullets = [_bullets]
        if len(_bullets) > 0:
            for b in _bullets:
                self.current_wave.players_scores[1].bullets_shot += 1
                self.bullets_group.add(b)
                
    def handle_grenades(self):
        #if current weapon has burst firemode and can shoot one more round
        _explode_cooked = False
        _now = datetime.datetime.now()
        if self.player.current_throwable.fuse_timeout_ms > 0 and self.player.current_throwable.cook_start_time != None and self.player.current_throwable.fuse_timeout_ms > 0 and _now > self.player.current_throwable.cook_start_time + datetime.timedelta(milliseconds=self.player.current_throwable.fuse_timeout_ms):
            _explode_cooked = True
        
        if ((pygame.K_g not in self.pressed_keys and self.player.current_throwable.cook_start_time == None)or\
            (pygame.K_g in self.pressed_keys and self.player.current_throwable.cook_start_time != None)) and not _explode_cooked:
            return
        
        def charge_kill_callback(hit_target):
            if hit_target:
                self.current_wave.players_scores[1].bullets_hit += 1
                
        if self.player.rolling:
            return
                
        if self.player.current_throwable.cook_start_time == None and not self.player.current_weapon.reloading:
            self.player.current_throwable.cook_grenade()
            return
        
        
        
        _charges = self.player.throw_grenade(kill_callback = charge_kill_callback)
            
        if pygame.K_g in self.pressed_keys:
            self.pressed_keys.remove(pygame.K_g)
        
        if _charges == None:
            return

        if type(_charges) != list:
            _charges = [_charges]
        for c in _charges:
            self.current_wave.players_scores[1].bullets_shot += 1
            self.bullets_group.add(c)
            if _explode_cooked:
                c.destroy()
    

    def update(self, **kwargs):
        events = kwargs.pop("events", None)
        
        if self.current_wave != None:
            if self.current_wave.started and not self.current_wave.loaded:
                return
        
        if not pygame.mixer.music.get_busy() and self.focused:
            mc.play_music(resources.get_song(resources.Songs.WAVE_1), 0.1, -1)
        
        game_controller.handle_events(self, events)
        
        if self.pause_screen != None and self.pause_screen.active:
            if self.player.reload_popup != None:
                self.player.reload_popup.destroy()
                self.player.reload_popup = None
            self.pause_screen.update()
            if self.client_type == enums.ClientType.SINGLE:
                return
        
        #input
        if pygame.K_p in self.pressed_keys:
            self.pause_screen.show()
            self.pressed_keys.remove(pygame.K_p)
        if pygame.K_ESCAPE in self.pressed_keys:
            self.pause_screen.show()
            self.pressed_keys.remove(pygame.K_ESCAPE)
        if pygame.K_r in self.pressed_keys:
            self.player.reload_weapon()
            self.pressed_keys.remove(pygame.K_r)
        if pygame.K_1 in self.pressed_keys:
            self.player.change_weapon(0)
            self.pressed_keys.remove(pygame.K_1)
        if pygame.K_2 in self.pressed_keys:
            self.player.change_weapon(1)
            self.pressed_keys.remove(pygame.K_2)
        if "wheel_1" in self.pressed_keys or "wheel_-1" in self.pressed_keys:
            self.player.change_weapon()
        
        self.handle_shooting()
        
        self.handle_grenades()
        
        if self.wave_summary != None:
            self.focused = False
            self.wave_summary.update(events = events)
            # if wave interval is out or p1 is ready and is singleplayer or both players are ready
            if self.wave_summary.timed_out or (self.wave_summary.p1_ready and (self.wave_summary.p2_ready or self.client_type == enums.ClientType.SINGLE)):
                self.next_wave()
            return
            
        # p1
        self.player.update(game = self)
        # p2
        if self.client_type != enums.ClientType.SINGLE:
            self.player2.update(game = self)
        # wave logic
        self.current_wave.update()
        # enemies
        if self.player.is_alive or (self.client_type != enums.ClientType.SINGLE and self.player2.is_alive):
            self.current_wave.update_enemies()
        else:
            if self.game_over_time == None:
                self.game_over()
            if self.game_over_popup._current_text_color[3] == 255:
                self.pause_screen.show()
        
        self.collision_group.update(group_name = "collision")
        self.jumpable_group.update(group_name = "jumpable")
    
        self.process_gravitables()    
            
        self.bullets_group.update(offset = self.player.offset_camera, game = self)
        
        self.center_camera()
        
        if "wheel_1" in self.pressed_keys:
            self.pressed_keys.remove("wheel_1")
        if "wheel_-1" in self.pressed_keys:
            self.pressed_keys.remove("wheel_-1")
        
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
        if pygame.K_l in self.pressed_keys:
            self.restart_game()
        if pygame.K_END in self.pressed_keys:
            self.current_wave.force_end()
            self.pressed_keys.remove(pygame.K_END)
        if pygame.K_m in self.pressed_keys and pygame.K_LCTRL in self.pressed_keys:
            match self.player.current_weapon.bullet_type:
                case enums.BulletType.PISTOL:
                    self.player.backpack.set_ammo(self.player.backpack.max_pistol_ammo, enums.BulletType.PISTOL)
                case enums.BulletType.ASSAULT_RIFLE:
                    self.player.backpack.set_ammo(self.player.backpack.max_rifle_ammo, enums.BulletType.ASSAULT_RIFLE)
                case enums.BulletType.SHOTGUN:
                    self.player.backpack.set_ammo(self.player.backpack.max_shotgun_ammo, enums.BulletType.SHOTGUN)
                case enums.BulletType.SNIPER:
                    self.player.backpack.set_ammo(self.player.backpack.max_sniper_ammo, enums.BulletType.SNIPER)
                case enums.BulletType.ROCKET:
                    self.player.backpack.set_ammo(self.player.backpack.max_rocket_ammo, enums.BulletType.ROCKET)

            self.player.backpack.get_throwable(self.player.current_throwable.weapon_type).count = self.player.backpack.max_grenade_type
                    
            self.pressed_keys.remove(pygame.K_m)
            self.pressed_keys.remove(pygame.K_LCTRL)

        if self.player.pos.y > self.map.rect.height:
            self.player.rect.bottom = self.map.rect.bottom - self.map.floor_y
            self.player.pos = vec(self.player.rect.topleft)
            
        for enemy in self.current_wave.enemies_group.sprites():
            if enemy.rect.top > self.map.rect.height:
                enemy.rect.bottom = self.map.rect.bottom - self.map.floor_y
                enemy.pos = vec(enemy.rect.topleft)
            
        if self.client_type != enums.ClientType.SINGLE and self.player2.pos.y > self.map.rect.height:
            self.player2.pos.y = 0
            self.player2.update_rect()
            
        self.last_pressed_keys = self.pressed_keys.copy()
        
    
       
    def draw(self):
        
        if not self.current_wave.loaded:
            self.screen.fill(colors.BLACK)
            return
        
        # Map
        self.screen.blit(self.map.image, vec(self.map.rect.topleft) - self.player.offset_camera)
        
        if self.pause_screen != None and self.pause_screen.active:
            self.pause_screen.draw(self.screen)
            return
        
        if self.wave_summary != None:
            self.wave_summary.draw(self.screen)
            if self.player.reload_popup != None:
                self.player.reload_popup.destroy()
                self.player.reload_popup = None
            return
        
        def draw_players():
            # P1
            self.player.draw(self.screen, self.player.offset_camera)
            # P2
            if self.client_type != enums.ClientType.SINGLE:
                self.player2.draw(self.screen, self.player.offset_camera)
        
        draw_players()
        
        # Wave
        self.current_wave.draw(self.screen, self.player.offset_camera)
        # bullets
        for b in self.bullets_group:
            b.draw(self.screen, self.player.offset_camera)
            
        #ui
        if self.game_over_time == None:
            self.draw_ui()
        else:
            panel_color = mc.fade_in_color(colors.BLACK, 255, self.game_over_time, self.game_over_time + datetime.timedelta(milliseconds=3000))
            panel_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            panel_surface.fill(panel_color)
            self.screen.blit(panel_surface, (0,0))
            
            if panel_color[3] == 255:
                self.game_over_popup.show()
                
            draw_players()
                
            
            
        # self.blit_debug()
        
        
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
        
        