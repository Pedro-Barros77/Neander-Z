import pygame, datetime

from domain.services import game_controller
from domain.models.rectangle_sprite import Rectangle
from domain.models.enemy import Enemy
from pygame.math import Vector2 as vec
 

class Wave():
    def __init__(self, game, **kwargs):
        self.game = game
        self.enemies_count = 0
        self.enemies_group = pygame.sprite.Group()
        self.max_enemies = 0

        self.schedule_time: datetime.datetime = None
        self.schedule_interval = 0
        self.schedule_callback: function = None
        
    def set_schedule(self, interval_ms, callback):
        self.schedule_time = datetime.datetime.now()
        self.schedule_interval = interval_ms
        self. schedule_callback = callback
        
    def run_schedule(self):
        if datetime.datetime.now() > self.schedule_time + datetime.timedelta(milliseconds=self.schedule_interval):
            self.schedule_time = datetime.datetime.now()
            self.schedule_callback()

    def get_id(self):
        self.enemies_count += 1
        return self.enemies_count

    def spawn_enemy(self, enemy: Enemy):
        self.enemies_group.add(enemy)
        
    def start(self):
        #implemented by the child
        pass

    def update(self, **kwargs):
        self.enemies_group.update(group_name = "enemies", game = self.game, client_type = self.game.client_type)
        if self.schedule_time != None:
            self.run_schedule()
        #implemented by the child
        pass
    
    def draw(self, screen: pygame.Surface, offset: vec):
        for e in self.enemies_group.sprites():
            e.draw(screen, offset)
        