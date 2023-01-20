import pygame, datetime, threading, random

from domain.services import menu_controller, resources, assets_manager
from domain.models.rectangle_sprite import Rectangle
from domain.models.enemy import Enemy
from pygame.math import Vector2 as vec
from domain.utils import enums, constants
from domain.models.wave_result import WaveResult
from domain.models.ui.popup_text import Popup

from domain.content.enemies.z_roger import ZRoger
from domain.content.enemies.z_robert import ZRobert
from domain.content.enemies.z_ronaldo import ZRonaldo
from domain.content.enemies.z_rui import ZRui
from domain.content.enemies.z_raven import ZRaven  
from domain.content.enemies.z_raimundo import ZRaimundo  
from domain.content.enemies.z_ronald import ZRonald  
 

class Wave():
    def __init__(self, game, **kwargs):
        
        _enemies_dict: list[dict] = kwargs.pop("enemies", [])
        self.total_enemies = sum([e["count"] for e in _enemies_dict])
        self.enemy_types: list[enums.Enemies] = []
        _total_spawn_chance = sum([e["spawn_chance_multiplier"] for e in _enemies_dict])
        self.enemies: list[dict] = []
        self.enemies_spawn_chances: dict = {}
        self.enemies_max: dict = {}
        for e in _enemies_dict:
            _d = e.copy()
            _count = _d.pop("count", 0)
            _type = _d.pop("type", enums.Enemies.Z_ROGER)
            self.enemies_spawn_chances[_type] = (e["spawn_chance_multiplier"] * 100 / _total_spawn_chance)/100
            self.enemies_max[_type] = e["max_alive"]
            
            if _type not in self.enemy_types:
                self.enemy_types.append(_type)
                if _type == enums.Enemies.Z_RONALD and enums.Enemies.Z_RONALDO not in self.enemy_types:
                    self.enemy_types.append(enums.Enemies.Z_RONALDO)
            for _ in range(_count):
                self.enemies.append(e.copy())
                
        self.game = game
        self.wave_number = kwargs.pop("wave_number",0)
        self.wave_type = kwargs.pop("wave_type", enums.WaveType.SIMPLE)
        self.wave_message = kwargs.pop("wave_message", "")
        self.enemies_current_id = 0
        self.enemies_group = pygame.sprite.Group()
        self.enemies_hitbox_group = pygame.sprite.Group()
        self.money_multiplier = kwargs.pop("money_multiplier", 1)
        self.wave_interval_s = kwargs.pop("wave_interval_s", 15)
        self.start_delay_ms = kwargs.pop("start_delay_ms", 2000)
        self.end_delay_ms = kwargs.pop("end_delay_ms", 1500)
        self.spawn_timer_ms = kwargs.pop("spawn_timer_ms", 5000)
        self.timed_spawn_count = kwargs.pop("timed_spawn_count", 1)
       
        self.spawn_count = 0
        self.enemies_count = 0
        self.killed_enemies_count = 0
        self.started = False
        self.finished = False
        
        self.last_spawn_time: datetime = None
        self.start_time: datetime.datetime = None

        self.players_scores = {
            1: WaveResult(),
            2: WaveResult(),
        }
        
        self.delayed_finish_time: datetime.datetime = None
        self.assets_manager = assets_manager.AssetsManager(self.enemy_types)
        self.loaded = False

    def update(self, **kwargs):
        if self.finished:
            return
        
        if not self.loaded:
            return
        elif self.start_time == None:
            self.start_time = datetime.datetime.now()
        
        if datetime.datetime.now() < self.start_time + datetime.timedelta(milliseconds=self.start_delay_ms):
            return

        self.enemies_count = len(self.enemies_group.sprites())
    
        if self.delayed_finish_time != None and datetime.datetime.now() >= self.delayed_finish_time:
            self.end_wave()
    
    def draw(self, screen: pygame.Surface, offset: vec):
        for e in self.enemies_group.sprites():
            e.draw(screen, offset)

    def start(self):
        self.started = True
        thread = threading.Thread(target=self.load_resources)
        thread.start()
        
            
        title_popup = Popup(f"Wave {self.wave_number}", vec(0,0), **constants.POPUPS["wave_title"])
        menu_controller.popup(title_popup, center = True)
        
        if len(self.wave_message) > 0:
            message_popup = Popup(self.wave_message, vec(0,0), **constants.POPUPS["wave_message"])
            message_popup.rect.centerx = title_popup.rect.centerx
            message_popup.rect.top = title_popup.rect.bottom + 5
            menu_controller.popup(message_popup)

    def load_resources(self):
        self.assets_manager.load_resources()
        self.loaded = True


    def get_id(self):
        self.enemies_current_id += 1
        return self.enemies_current_id
    
    def create_enemy(self, enemy_type, pos:vec, enemy_dict):
        enemy = None
        match enemy_type:
            case enums.Enemies.Z_ROGER:
                enemy = ZRoger(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_ROBERT:
                enemy = ZRobert(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_RONALDO:
                enemy = ZRonaldo(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_RUI:
                enemy = ZRui(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_RAVEN:
                enemy = ZRaven(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_RAIMUNDO:
                enemy = ZRaimundo(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
            case enums.Enemies.Z_RONALD:
                enemy = ZRonald(pos, self, self.assets_manager, **enemy_dict, id = self.get_id())
        
        return enemy

    def spawn_enemy(self, enemy: Enemy):
        self.enemies_group.add(enemy)
        if enemy.hitbox_head != None:
            self.enemies_hitbox_group.add(enemy.hitbox_head)
        if enemy.hitbox_body != None:
            self.enemies_hitbox_group.add(enemy.hitbox_body)
            
        self.spawn_count += 1
        self.enemies_count += 1
        
        
        
    def delay_end_wave(self, delay_ms: float):
        if self.delayed_finish_time == None:
            self.delayed_finish_time = datetime.datetime.now() + datetime.timedelta(milliseconds=delay_ms)

    def end_wave(self):
        self.players_scores[1].money = (self.players_scores[1].score / 4) * self.money_multiplier
        self.players_scores[1].player_character = self.game.player.character
        self.players_scores[2].money = (self.players_scores[2].score / 4) * self.money_multiplier
        if self.game.client_type != enums.ClientType.SINGLE:
            self.players_scores[2].player_character = self.game.player2.character
        
        self.players_scores[1].wave_interval_s = self.wave_interval_s
        self.players_scores[1].wave_number = self.wave_number
        self.players_scores[2].wave_interval_s = self.wave_interval_s
        self.players_scores[2].wave_number = self.wave_number

        self.game.end_wave(self.players_scores)
        self.finished = True
        
    def kill_all(self):
        for e in self.enemies_group.sprites():
            if e.enemy_name != enums.Enemies.Z_RUI:
                e.take_damage(99999, 1, True)
        self.players_scores[1].bullets_shot += 1

    def handle_score(self, enemy: Enemy, attacker, headshot_kill = False):
        if attacker == None:
            return
        
        if attacker == 3:
            attacker = 1
            
        _new_score = enemy.kill_score
        if headshot_kill:
            _new_score *= enemy.headshot_score_multiplier

        self.players_scores[attacker].kills_count += 1
        if headshot_kill:
            self.players_scores[attacker].headshot_kills_count += 1
        
        if attacker == 1:
            self.game.player.score += _new_score 
        else:
            if self.game.client_type != enums.ClientType.SINGLE:
                self.game.player2.score += _new_score

        self.killed_enemies_count += 1
        self.players_scores[attacker].score += _new_score
        
    



            
    def update_enemies(self):
        self.enemies_group.update(group_name = "enemies", game = self.game, client_type = self.game.client_type)