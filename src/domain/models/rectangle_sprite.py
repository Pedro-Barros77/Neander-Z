import pygame

class Rectangle(pygame.sprite.Sprite):
    def __init__(self, size, pos, **kwargs):
        super().__init__()
        
        self.size = size
        """The width and height of the surface.""" 
        
        self.pos = pos
        """The position of the top-left corner of the surface.""" 
        
        self.image = pygame.Surface(size)
        """The map image/surface.""" 
        
        self.rect = self.image.get_rect()
        """The rectangle of the image.""" 
        
        self.name = kwargs.pop("name", "rectangle")
        	
        self.rect.topleft = self.pos
        
        self.last_rect = self.rect.copy()
        
    def update_rect(self):
        self.rect.topleft = self.pos
        
    def update_pos(self):
        self.pos = self.rect.topleft