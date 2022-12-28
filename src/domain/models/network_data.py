import ast
from pygame.math import Vector2 as vec

from domain.models.enemy import Enemy
from domain.content.weapons.small_bullet import SmallBullet
from domain.models.wave_result import WaveResult
from domain.utils import enums
from domain.services import game_controller

class Data:
    def __init__(self, **kwargs):
        self.enemies = []
        self.bullets = []
        self.wave_results = kwargs.pop("wave_results", [])
        
        self.player_rect = kwargs.pop("player_rect", (0,0, 1,1))
        self.player_speed = kwargs.pop("player_speed", (0,0))
        self.player_acceleration = kwargs.pop("player_acceleration", (0,0))
        self.player_last_rect = kwargs.pop("player_last_rect", self.player_rect)
        self.player_health = kwargs.pop("player_health", 0)
        
        self.player2_score = kwargs.pop("player2_score", 0)
        self.player_wave_ready = kwargs.pop("player_wave_ready", False)
        
        #animation
        self.player_turning_dir = kwargs.pop("player_turning_dir", 0)
        self.player_jumping = kwargs.pop("player_jumping", False)
        self.player_running = kwargs.pop("player_running", False)
        self.player_falling_ground = kwargs.pop("player_falling_ground", False)
        self.player_firing = kwargs.pop("player_firing", False)
        
        self.player_mouse_pos = kwargs.pop("player_mouse_pos", (0,0))
        self.player_aim_angle = kwargs.pop("player_aim_angle", 0)
        
        self.net_id = kwargs.pop("net_id", 0)
        self.command_id = kwargs.pop("command_id", 0)
        
        
        
        if game_controller._enemy_netdata_keys == None:
            game_controller._enemy_netdata_keys = list(Enemy((0,0),enums.Enemies.Z_ROGER, None).get_netdata().keys())
        if game_controller._bullet_netdata_keys == None:
            game_controller._bullet_netdata_keys = list(SmallBullet(vec(0,0),0,0,0,0,0).get_netdata().keys())
        if game_controller._waveresult_netdata_keys == None:
            game_controller._waveresult_netdata_keys = list(WaveResult().get_netdata().keys())
    
    def _get_values(self, val):
        if type(val) == dict:
            return self._get_values_dict(val)
        elif type(val) == list:
            return self._get_values_list(val)
        else:
            return val
    
    def _get_values_dict(self, source: dict):
        result = []
        for val in source.values():
            result.append(self._get_values(val))
        
        return result
    
    def _get_values_list(self, source: list):
        result = []
        for val in source:
            result.append(self._get_values(val))
        
        return result
    
    def _get_buffer(self):
        result= []
        attributes = [a for a in self.__dict__.keys() if not a.startswith('_')]
        
        for att in attributes:
            val = getattr(self, att)
            
            result.append(self._get_values(val))
        
        return str(result).encode('utf-8')
        
    def _load_buffer(self, buff: bytes):
        string = buff.decode('utf-8')
        array: list = ast.literal_eval(string)
        
        attributes = [a for a in self.__dict__.keys() if not a.startswith('_')]
        for i, att in enumerate(attributes):
            if type(getattr(self, att)) != list:
                setattr(self, att, array[i])
        
        self.enemies = []
        self.bullets = []
        self.wave_results = []
            
        for i, enemy in enumerate(array[0]):
            self.enemies.append({})
            for v, en_val in enumerate(enemy):
                self.enemies[i][game_controller._enemy_netdata_keys[v]] = en_val
                
        for i, bullet in enumerate(array[1]):
            self.bullets.append({})
            for v, b_val in enumerate(bullet):
                self.bullets[i][game_controller._bullet_netdata_keys[v]] = b_val

        for i, result in enumerate(array[2]):
            self.wave_results.append({})
            for v, res_val in enumerate(result):
                self.wave_results[i][game_controller._waveresult_netdata_keys[v]] = res_val