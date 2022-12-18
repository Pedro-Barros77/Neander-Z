import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors

class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, image_path: str, pos: vec, angle: float, speed: float):
        
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.angle = angle
        self.speed = speed
        
    
    def draw(self, screen: pygame.Surface):
        print("drawing")
        # screen.blit(self.image, self.rect)
        # pygame.draw.circle(screen, colors.RED, self.rect.topleft, 15, 2)
        
    def move(self):
        # print("moving")
        
        return False