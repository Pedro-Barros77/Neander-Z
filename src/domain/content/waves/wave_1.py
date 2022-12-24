import pygame, random

from domain.services import game_controller
from domain.models.wave import Wave
from domain.utils import enums
from domain.content.enemies.z_roger import ZRoger

class Wave_1(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        self.max_alive_enemies = 5
        self.wave_step = 3
        self.total_enemies = 10   
        self.current_wave_step = self.wave_step
          
        self.roger_data = {
            "movement_speed": 0.12,
            "health": 30
        }

    def update(self, **kwargs):
        if not self.started or self.finished:
            return

        super().update(**kwargs)

        if self.spawn_count >= self.total_enemies:
            if self.enemies_count == 0:
                self.end_wave()
        
        elif self.current_wave_step >= self.wave_step:
            self.current_wave_step = 0
            self.spawn()
        #self.spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = get_id(), attack_targets = [game.players_group]))

    def start(self):
        super().start()

             
       
        
    def spawn(self):

        
        #if alive zumbi is smaller than max 
        while self.enemies_count < self.max_alive_enemies and self.spawn_count < self.total_enemies:
            
            radx = random.randint(0, self.game.map.rect.width - 50)
            y = self.game.map.rect.bottom - (self.game.map.floor_y + 10) - 100
            self.spawn_enemy( ZRoger((radx,y), enums.Enemies.Z_ROGER,self, **self.roger_data, id = self.get_id()))
            self.spawn_count += 1
            self.enemies_count += 1
