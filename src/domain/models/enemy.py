import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants
from domain.services import game_controller
from domain.models.progress_bar import ProgressBar



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        
        self.name = "enemy"
        self.jump_force = 12
        self.damage = 1
        
        self.pos: vec = vec((pos))
        self.speed = vec(0,0)
        self.acceleration: vec = vec(0,0)
        self.dir: vec = vec(0,0)
        self.last_dir: vec = self.dir.copy()
        
        self.image = game_controller.scale_image(pygame.image.load(image), 2)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
        self.health_bar = ProgressBar(30, pygame.Rect(self.pos - vec(0,-15), (self.rect.width * 1.3, 7)), border_width = 1, border_color = colors.LIGHT_GRAY, value_anim_speed = 0.2)
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
        
    def update(self):
        self.health_bar.update()
        
    def draw(self, surface: pygame.Surface, offset: vec):
        self.health_bar.rect.center = vec(self.rect.centerx, self.rect.top - 15) - offset
        surface.blit(self.image, self.pos - offset)
        self.health_bar.draw(surface)
        
    def take_damage(self, value: float):
        self.health_bar.remove_value(value)
        
    def get_health(self, value: float):
        self.health_bar.add_value(value)