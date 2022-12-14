import pygame

from domain.utils import colors

class Drawer:
    def __init__(self, game):
        self.game = game    
    
    def draw_text(self, text, pos, color = colors.WHITE, size = 30, font = 'Arial'):
        text_surface = self.get_text_surface(text, color, size, font)
        self.game.screen.blit(text_surface, pos)
    
    def get_text_surface(self, text, color, size, font):
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