import pygame, random

from domain.services import game_controller
from domain.models.wave import Wave
from domain.utils import enums
from domain.content.enemies.z_roger import ZRoger

class Wave_1(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)

        
        self.roger_data = {
            "movement_speed": 0.12,
            "id": self.get_id()
        }

    def update(self, **kwargs):
        super().update(**kwargs)
        #self.spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = get_id(), attack_targets = [game.players_group]))

    def start(self):
        self.spawn()
        self.set_schedule(800, self.spawn)
        
    def spawn(self):
        self.spawn_enemy( ZRoger((random.randint(0, self.game.map.rect.width - 50),self.game.map.rect.bottom - (self.game.map.floor_y + 10) - 100), enums.Enemies.Z_ROGER, **self.roger_data))