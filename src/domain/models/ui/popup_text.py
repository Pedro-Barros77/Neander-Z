import pygame, datetime
from pygame.math import Vector2 as vec

from domain.utils import colors

class Popup(pygame.sprite.Sprite):
    def __init__(self, text: str, pos: vec, timout_ms: float, **kwargs) -> None:
        super().__init__()
        
        self.text = text
        self.timeout_ms = timout_ms
        self.text_color = kwargs.pop("text_color", colors.RED)
        self.background_color = kwargs.pop("background_color", (0,0,0))
        self.border_color = kwargs.pop("border_color", (0,0,0))
        self.border_width = kwargs.pop("border_width", 0)
        self.font = kwargs.pop("font", pygame.font.SysFont('arial', 12))
        self.fade_in_ms = kwargs.pop("fade_in_ms", 0)
        self.fade_out_ms = kwargs.pop("fade_out_ms", 0.8)
        self.scale_anim_size = kwargs.pop("scale_anim_size", 1.2)
        self.visible = False
        self.timed_out = False
        
        self.current_text_color = colors.add_alpha(self.text_color)
        self.current_background_color = colors.add_alpha(self.background_color, 0)
        self.current_border_color = colors.add_alpha(self.border_color, 0)
        
        self.image = self.rerender()
        self.rect = pygame.Rect(pos, self.image.get_size())
        self.show_time: datetime.datetime = None
        
        self.show_on_init = kwargs.pop("show_on_init", True)
        if self.show_on_init:
            self.show()
            
    def rerender(self):
        return self.font.render(self.text, True, self.current_text_color, self.current_border_color)
        
    def destroy(self):
        self.visible = False
        self.timed_out = True
        self.kill()
        
    def show(self):
        self.visible = True
        self.show_time = datetime.datetime.now()
    
    def update(self, **kwargs):
        if not self.visible:
            return
        
        _deadline = self.show_time + datetime.timedelta(milliseconds= self.timeout_ms)
        self.timed_out = datetime.datetime.now() > _deadline
            
        if self.timed_out:
            if self.fade_out_ms > 0 and self.current_text_color[3] > 0:
                anim_start = (_deadline - datetime.timedelta(milliseconds=self.fade_out_ms))
                self.current_background_color = self.fade_out(self.background_color, anim_start, _deadline)
                self.current_text_color = self.fade_out(self.text_color, anim_start, _deadline)
                self.current_border_color = self.fade_out(self.border_color, anim_start, _deadline)
            else:
                self.destroy()
                
                
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        self.image = self.rerender()
        screen.blit(self.image, self.rect)
        
        
        
        
    def fade_out(self, color: tuple[int,int,int], start_time: datetime.datetime, end_time: datetime.datetime):
        
        now = datetime.datetime.now().timestamp()
        end = end_time.timestamp()
        start = start_time.timestamp()
        
        if start > now:
            return colors.add_alpha(color, 255)
        
        percentage = ((now - start) / (end - start)) * 100
        alpha = (255*(100-percentage))/100
        
        return colors.add_alpha(color, int(alpha))
        