import pygame

from domain.services import game_controller
from domain.models.rectangle_sprite import Rectangle
from domain.utils import enums

class Map(pygame.sprite.Sprite):
    def __init__(self, screen, image, **kwargs):
        super().__init__()
        self.pos = (0,0)
        """The position of the top-left corner of the map image.""" 
               
        self.floor_y = kwargs.pop("floor_y", 20)
        """The vertical distance from the bottom of the screen to the map floor.""" 
        
        self.image = game_controller.scale_image(pygame.image.load(image), 1.5, convert_type=enums.ConvertType.CONVERT)
        """The map image/surface.""" 
        
        self.size = self.image.get_size()
        """The width and height of the image.""" 
        	
        self.rect = self.image.get_rect()
        """The rectangle of the image.""" 
        self.rect.topleft = self.pos
        
        self.floor = Rectangle((self.size[0], 200), (0, screen.get_height() - self.floor_y), name = "floor")
        """A rectangle representing the floor of the map."""  

        self.left_wall = Rectangle((10, screen.get_height()), (0, 0), name = "left_wall")
        """A rectangle representing the left wall of the map."""  
        
        self.right_wall = Rectangle((10, screen.get_height()), (self.rect.right - 10, 0), name = "right_wall")
        """A rectangle representing the right wall of the map."""  
        
        
    def update_rect(self):
        self.rect.topleft = self.pos
        
    def update_pos(self):
        self.pos = self.rect.topleft