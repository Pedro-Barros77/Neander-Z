import pygame, random

from domain.services import menu_controller, resources
from domain.models.wave import Wave
from domain.utils import enums
from domain.content.enemies.z_roger import ZRoger
from domain.content.enemies.z_robert import ZRobert

class SimpleWave(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        
        self.wave_type = enums.WaveType.SIMPLE
        self.wave_number = kwargs.pop("wave_number", 1)
        self.max_alive_enemies = kwargs.pop("max_alive_enemies", 5)
        self.wave_step = kwargs.pop("wave_step", 3)
        self.current_wave_step = self.wave_step
        self.wave_interval_s = kwargs.pop("wave_interval_s", 60)
        
        self.health_rand_margin = 0.3
        self.speed_rand_margin = 0.2
        self.damage_rand_margin = 0.3
          
    def update(self, **kwargs):
        if not self.started or self.finished:
            return

        super().update(**kwargs)

        if self.spawn_count >= self.total_enemies:
            if self.enemies_count == 0:
                self.delay_end_wave(1500)
        
        elif self.current_wave_step >= self.wave_step:
            self.current_wave_step = 0
            self.spawn()

    def start(self):
        super().start()
        

    def get_random_enemy(self) -> dict:
        e_dict = self.enemies[random.randint(0, len(self.enemies)-1)].copy()
        self.enemies.remove(e_dict)
        
        _health_margin = e_dict["health"]*self.health_rand_margin
        _health = e_dict["health"]
        e_dict["health"] = round(random.uniform(_health - _health_margin, _health + _health_margin), 2)

        _speed_margin = e_dict["movement_speed"]*self.speed_rand_margin
        _speed = e_dict["movement_speed"]
        e_dict["movement_speed"] = round(random.uniform(_speed - _speed_margin, _speed + _speed_margin), 2)

        _damage_margin = e_dict["damage"]*self.damage_rand_margin
        _damage = e_dict["damage"]
        e_dict["damage"] = round(random.uniform(_damage - _damage_margin, _damage + _damage_margin), 2)
        
        return e_dict

    def spawn(self):
        #if alive zumbi is smaller than max 
        while self.enemies_count < self.max_alive_enemies and self.spawn_count < self.total_enemies:
            
            radnx = random.randint(0, self.game.map.rect.width - 50)
            y = self.game.map.rect.bottom - (self.game.map.floor_y + 10 + 40) - 100
            _enemy_dict = self.get_random_enemy()
            _type = _enemy_dict.pop("type", enums.Enemies.Z_ROGER)
            
            match _type:
                case enums.Enemies.Z_ROGER:
                    self.spawn_enemy( ZRoger((radnx,y), self, **_enemy_dict, id = self.get_id()))
                case enums.Enemies.Z_ROBERT:
                    self.spawn_enemy( ZRobert((radnx,y), self, **_enemy_dict, id = self.get_id()))
            
            self.spawn_count += 1
            self.enemies_count += 1
