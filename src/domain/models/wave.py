import pygame

from domain.services import game_controller
from domain.models.rectangle_sprite import Rectangle
from models.enemy import Enemy
 

class Wave():
    def __init__(self, screen, **kwargs):
        self.enemies_count = 0
        self.enemies_group = pygame.sprite.Group()

    def get_id(self):
        self.enemies_count += 1
        return self.enemies_count

    def spawn_enemy(self, enemy: Enemy):
        self.enemies_group.add(enemy)

    def update(self, **kwargs):
        pass