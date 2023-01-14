import pygame, random, datetime
from pygame.math import Vector2 as vec

from domain.services import menu_controller, resources
from domain.models.wave import Wave
from domain.utils import enums
from domain.models.enemy import Enemy

class BossWave(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        
        self.wave_type = enums.WaveType.BOSS
        self.wave_number = kwargs.pop("wave_number", 1)
        self.max_alive_enemies = kwargs.pop("max_alive_enemies", 5)
        self.current_wave_step = self.wave_step
        self.wave_interval_s = kwargs.pop("wave_interval_s", 60)
        self.spawn_timer_ms = kwargs.pop("spawn_timer_ms", 5000)
        self.timed_spawn_count = kwargs.pop("timed_spawn_count", 1)
        
        self.boss: Enemy = None
        
        self.last_spawn_time: datetime = None
        
        self.health_rand_margin = 0.3
        self.speed_rand_margin = 0.2
        self.damage_rand_margin = 0.3
          
    def update(self, **kwargs):
        if not self.started or self.finished or datetime.datetime.now() < self.start_time + datetime.timedelta(milliseconds=self.start_delay_ms):
            return

        super().update(**kwargs)
        
        if self.boss == None:
            self.spawn()
        else:
            if not self.boss.is_alive and self.enemies_count == 0:
                self.delay_end_wave(1500)
            
            elif (self.last_spawn_time == None or datetime.datetime.now() >= self.last_spawn_time + datetime.timedelta(milliseconds=self.spawn_timer_ms)) and self.boss.is_alive:
                self.current_wave_step = 0
                self.spawn()
                self.last_spawn_time = datetime.datetime.now()

    def start(self):
        super().start()
        

    def get_random_enemy(self) -> dict:
        e_dict = self.enemies[random.randint(0, len(self.enemies)-1)].copy()
        
        if not self.boss.is_alive:
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
        for _ in range(self.timed_spawn_count):
            
            floor_y = self.game.map.rect.bottom - self.game.map.floor_y
            can_spawn = False
            min_distance = 500
            rand_x = 0
            while not can_spawn:
                rand_x = random.randint(0, self.game.map.rect.width - 50)
                can_spawn = vec(self.game.player.rect.centerx, floor_y).distance_to(vec(rand_x, floor_y)) > min_distance

            if self.boss == None:
                _enemy_dict = self.enemies[0]
                self.enemies = self.enemies[1:]
            else:
                _enemy_dict = self.get_random_enemy()
                
            _type = _enemy_dict.pop("type", enums.Enemies.Z_ROGER)
            
            enemy = self.create_enemy(_type, (rand_x,0), _enemy_dict)
            
            if enemy != None:
                enemy.rect.bottom = floor_y
                enemy.pos = vec(enemy.rect.topleft)
                enemy.start_pos = enemy.pos.copy()
                self.spawn_enemy(enemy)
                if self.boss == None:
                    self.boss = enemy
            
            self.spawn_count += 1
            self.enemies_count += 1
