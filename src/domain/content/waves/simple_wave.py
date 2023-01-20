import pygame, random, datetime
from pygame.math import Vector2 as vec

from domain.services import menu_controller, resources
from domain.models.wave import Wave
from domain.utils import enums
from domain.content.enemies.z_roger import ZRoger
from domain.content.enemies.z_robert import ZRobert
from domain.content.enemies.z_ronaldo import ZRonaldo
from domain.content.enemies.z_rui import ZRui

class SimpleWave(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        
        self.wave_type = enums.WaveType.SIMPLE
        self.wave_number = kwargs.pop("wave_number", 1)
        self.wave_interval_s = kwargs.pop("wave_interval_s", 60)
        
        self.health_rand_margin = 0.3
        self.speed_rand_margin = 0.2
        self.damage_rand_margin = 0.3
          
    def update(self, **kwargs):
        super().update(**kwargs)

        if not self.started or self.finished or datetime.datetime.now() < self.start_time + datetime.timedelta(milliseconds=self.start_delay_ms) or not self.loaded:
            return

        if self.spawn_count >= self.total_enemies:
            if self.enemies_count == 0:
                self.delay_end_wave(self.end_delay_ms)
        
        if (self.last_spawn_time == None or datetime.datetime.now() >= self.last_spawn_time + datetime.timedelta(milliseconds=self.spawn_timer_ms))\
            or len(self.enemies_group.sprites()) == 0:
            self.spawn()
            self.last_spawn_time = datetime.datetime.now()

    def start(self):
        super().start()
        

    def get_random_enemy(self) -> dict | None:
        _choice, _type = None, None
        
        while (_choice == None or len(_choice) == 0):
            if len(self.enemies_spawn_chances.keys()) == 0:
                return None
            
            _type = random.choices(population=list(self.enemies_spawn_chances.keys()), weights=list(self.enemies_spawn_chances.values()))[0]
            _choice = [e for e in self.enemies if e["type"] == _type]
            _max = self.enemies_max[_type]
            
            #if there's no enemy of that type to spawn, remove from chances and start over
            if len(_choice) == 0:
                self.enemies_spawn_chances.pop(_type)

            #if that enemy type has reached MAX
            if len([e for e in self.enemies_group.sprites() if e.enemy_name == _type]) >= _max:
                _choice = None
                #if it's the only type left to spawn, return
                if len(self.enemies_spawn_chances.keys()) <= 1:
                    return None
        
        e_dict = _choice[0].copy()
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
        if self.spawn_count >= self.total_enemies:
            return
        
        _count = self.timed_spawn_count
        if self.spawn_count + _count > self.total_enemies:
            _count = self.total_enemies - self.spawn_count
            
        for _ in range(_count):
            floor_y = self.game.map.rect.bottom - self.game.map.floor_y
            can_spawn = False
            min_distance = 500
            rand_x = 0
            while not can_spawn:
                rand_x = random.randint(0, self.game.map.rect.width - 50)
                can_spawn = vec(self.game.player.rect.centerx, floor_y).distance_to(vec(rand_x, floor_y)) > min_distance

            _enemy_dict = self.get_random_enemy()
            if _enemy_dict == None:
                return
            
            _type = _enemy_dict.pop("type", enums.Enemies.Z_ROGER)
            
            enemy = self.create_enemy(_type, (rand_x,floor_y), _enemy_dict)
            
            if enemy != None:
                enemy.rect.bottom = floor_y
                enemy.pos = vec(enemy.rect.topleft)
                enemy.start_pos = enemy.pos.copy()
                self.spawn_enemy(enemy)