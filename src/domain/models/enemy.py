import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, enums, constants
from domain.services import game_controller
from domain.models.progress_bar import ProgressBar



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_name: enums.Enemies, **kwargs):
        super().__init__()
        
        self.name = "enemy"
        self.jump_force = 12
        self.damage = 1
        self.enemy_name = enemy_name
        self.image_scale = 2
        self.movement_speed = kwargs.pop("movement_speed", 5)
        
        self.pos: vec = vec((pos))
        self.speed = vec(0,0)
        self.acceleration: vec = vec(0,0)
        self.dir: vec = vec(0,0)
        self.last_dir: vec = self.dir.copy()
        
        self.is_alive = True
        
        self.running = True
        """If the running animation is running."""
        self.running_frame = 0
        """The current frame index of the running animation."""
        run_folder = constants.get_zombie_frames(self.enemy_name, enums.AnimActions.RUN)
        self.run_frames = game_controller.load_sprites(run_folder)
        
        self.image = game_controller.scale_image(self.run_frames[0], self.image_scale)
        self.size = self.image.get_size()
        	
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
        self.health_bar = ProgressBar(30, pygame.Rect(self.pos - vec(0,-15), (self.rect.width * 1.3, 7)), border_width = 1, border_color = colors.LIGHT_GRAY, value_anim_speed = 0.2)
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
        
    def draw(self, surface: pygame.Surface, offset: vec):
        self.health_bar.rect.center = vec(self.rect.centerx, self.rect.top - 15) - offset
        surface.blit(self.image, self.pos - offset)
        self.health_bar.draw(surface)
        
    def take_damage(self, value: float):
        self.health_bar.remove_value(value)
        if self.health_bar.target_value <= 0:
            self.is_alive = False
            
        
    def get_health(self, value: float):
        self.health_bar.add_value(value)