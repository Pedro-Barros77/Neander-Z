import pygame, random

from domain.services import game_controller
from domain.models.wave import Wave
from domain.utils import enums
from domain.content.enemies.z_roger import ZRoger

class Wave_1(Wave):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        self.max_enemies = 5
        
        self.roger_data = {
            "movement_speed": 0.12,
            "health": 30
        }

    def update(self, **kwargs):
        super().update(**kwargs)
        #self.spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = get_id(), attack_targets = [game.players_group]))

    def start(self):
        self.spawn()
        if self.game.client_type != enums.ClientType.GUEST:
            self.set_schedule(500, self.spawn)
        
    def spawn(self):
        if len(self.enemies_group.sprites()) < self.max_enemies:
            radx = random.randint(0, self.game.map.rect.width - 50)
            y = self.game.map.rect.bottom - (self.game.map.floor_y + 10) - 100
            self.spawn_enemy( ZRoger((200,y), enums.Enemies.Z_ROGER, **self.roger_data, id = self.get_id()))