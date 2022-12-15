import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors

class Drawer:
    def __init__(self, game):
        self.game = game    
    
    def draw_text(self, text: str, pos: tuple[int,int], color = colors.WHITE, size = 30, font = 'Arial'):
        """Draws a text on the screen.

        Args:
            text (str): The text to be drawn.
            pos (tuple[int,int]): The topleft corner of the position to draw the text.
            color (tuple[int,int,int], optional): The RGB color to fill the text. Defaults to colors.WHITE.
            size (int, optional): The font size. Defaults to 30.
            font (str, optional): The font name. Defaults to 'Arial'.
        """        
        text_surface = self.get_text_surface(text, color, size, font)
        self.game.screen.blit(text_surface, pos)
    
    def get_text_surface(self, text: str, color: tuple[int,int,int], size: int, font: str | pygame.font.Font):
        """Creates the surface of a text without drawing it.

        Args:
            text (str): The text to be created.
            color (tuple[int,int,int]): The RGB color to fill the text.
            size (int): The font size.
            font (str | pygame.font.Font): The font name or object to use on text.

        Returns:
            pygame.Surface: The surface of the text.
        """        
        text = str(text)
        
        r, g, b, *a = color
        color = (r,g,b)
        _font = None
        
        if type(font) == str:
            _font = pygame.font.SysFont(font, size)
        else:
            _font = font
                
        text_surface = _font.render(text, False, color)
        if len(a) > 0:
            text_surface.set_alpha(a[0])
        return text_surface
    
    def draw_enemies(self, surface: pygame.Surface, enemies: pygame.sprite.Group):
        for e in enemies:
            surface.blit(e.image, e.pos - self.game.player.offset_camera)
            
    
    def draw_line(self, start: vec, end: vec):
        pygame.draw.line(self.game.screen, colors.RED, start, end, width=2)