import pygame, datetime

from domain.services import menu_controller, resources
from domain.models.rectangle_sprite import Rectangle
from domain.models.enemy import Enemy
from pygame.math import Vector2 as vec
from domain.utils import enums, constants
from domain.models.wave_result import WaveResult
from domain.models.ui.popup_text import Popup
 

class Wave():
    def __init__(self, game, **kwargs):
        
        _enemies_dict: list[dict] = kwargs.pop("enemies", [])
        self.total_enemies = sum([e["count"] for e in _enemies_dict])
        
        self.enemies: list[dict] = []
        for e in _enemies_dict:
            _count = e.copy().pop("count", 0)
            for _ in range(_count):
                self.enemies.append(e)
        
        self.game = game
        self.wave_number = kwargs.pop("wave_number",0)
        self.wave_type = kwargs.pop("wave_type", enums.WaveType.SIMPLE)
        self.enemies_current_id = 0
        self.enemies_group = pygame.sprite.Group()
        self.enemies_hitbox_group = pygame.sprite.Group()
        self.max_alive_enemies = kwargs.pop("max_alive_enemies", 5)
        self.wave_step = kwargs.pop("wave_step", 1)
        self.current_wave_step = kwargs.pop("current_wave_step", 0)
        self.money_multiplier = kwargs.pop("money_multiplier", 1.8)
        self.wave_interval_s = kwargs.pop("wave_interval_s", 15)
        self.spawn_count = 0
        self.enemies_count = 0
        self.started = False
        self.finished = False

        self.players_scores = {
            1: WaveResult(),
            2: WaveResult(),
        }
        
        self.delayed_finish_time: datetime.datetime = None


    def get_id(self):
        self.enemies_current_id += 1
        return self.enemies_current_id

    def spawn_enemy(self, enemy: Enemy):
        self.enemies_group.add(enemy)
        if enemy.hitbox_head != None:
            self.enemies_hitbox_group.add(enemy.hitbox_head)
        if enemy.hitbox_body != None:
            self.enemies_hitbox_group.add(enemy.hitbox_body)
        
    def start(self):
        if self.game.client_type == enums.ClientType.SINGLE:
            self.money_multiplier = 1
        self.started = True
        # menu_controller.popup(Popup(f"Wave {self.wave_number}", vec(0,0), **constants.POPUPS["wave_title"]), center = True)
        
        
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
        self.players_scores[2].wave_interval_s = self.wave_interval_s

        self.game.end_wave(self.players_scores)
        self.finished = True
        
    def kill_all(self):
        for e in self.enemies_group.sprites():
            e.kill(1)

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

        self.players_scores[attacker].score += _new_score
        




    def update(self, **kwargs):
        if self.finished:
            return
        self.enemies_count = len(self.enemies_group.sprites())
    
        if self.delayed_finish_time != None and datetime.datetime.now() >= self.delayed_finish_time:
            self.end_wave()
    
    def draw(self, screen: pygame.Surface, offset: vec):
        for e in self.enemies_group.sprites():
            e.draw(screen, offset)
            
    def update_enemies(self):
        self.enemies_group.update(group_name = "enemies", game = self.game, client_type = self.game.client_type)