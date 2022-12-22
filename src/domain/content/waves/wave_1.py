import pygame

from domain.services import game_controller
from domain.models.rectangle_sprite import Rectangle
from models.wave import Wave

class Wave_1(Wave):
    def __init__(self, screen, **kwargs):
        super().__init__(screen, **kwargs)


    def update(self, **kwargs):
        super().update(**kwargs)
        #self.spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = get_id(), attack_targets = [game.players_group]))

