import pygame, datetime
from pygame.math import Vector2 as vec

from domain.utils import colors, math_utillity as math

class Popup(pygame.sprite.Sprite):
    def __init__(self, text: str, pos: vec, **kwargs) -> None:
        super().__init__()
        
        self.name = kwargs.pop("name", None)
        """A string to represent this popup. Used when 'unique' is true to prevent repeated popups."""
        self.unique = kwargs.pop("unique", False)
        """If set to True, no more popups with the same name will be added to the group as long this exists."""
        
        self.start_pos: vec = pos
        """The starting position of the text."""
        self.text = text
        """The text to be shown in the popup."""
        self.timeout_ms = kwargs.pop("timeout_ms", None)
        """The time in milliseconds to wait since show() to call hide(). Defaults to 0."""
        self.text_color = kwargs.pop("text_color", colors.WHITE)
        """The color of the text. Defaults to colors.White."""
        self.background_color = kwargs.pop("background_color", None)
        """The background color of the text box. Defaults to None."""
        self.border_color = kwargs.pop("border_color", None)
        """The color of the text box borders. Defaults to None."""
        self.border_width = kwargs.pop("border_width", 0)
        """The width of the text box borders. Defaults to 0."""
        self.padding: vec = kwargs.pop("padding", vec(5,2))
        """The distance between the text box borders and the text. Defaults to vec(5,2)."""
        self.font = kwargs.pop("font", pygame.font.SysFont('arial', 12))
        """The font of the text. Defaults to Arial 12."""
        self.fade_in_ms = kwargs.pop("fade_in_ms", 0)
        """The time in milliseconds to animate the fade in effect. Defaults to 0."""
        self.fade_out_ms = kwargs.pop("fade_out_ms", 0)
        """The time in milliseconds to animate the fade out effect. Defaults to 0."""
        self.float_anim_distance = kwargs.pop("float_anim_distance", 0)
        """The distance to float up with fade out animation. Defaults to 0."""
        self.show_on_init = kwargs.pop("show_on_init", True)
        """If the method show() should be called after initialization. Defaults to True."""
        self.rect = pygame.Rect(pos, self.font.render(self.text, True, colors.WHITE).get_size())
        """The rect of the popup text box."""
        self.rect.size = vec(self.rect.size) + (self.padding *2) + vec(self.border_width, self.border_width)*2
        
        self._current_text_color = self.text_color
        self._current_background_color = self.background_color
        self._current_border_color = self.border_color
        
        self.image = self.rerender()
        """The surface of the popup."""
        
        self._show_time: datetime.datetime = None
        self._hide_time: datetime.datetime = None
        
        if self.show_on_init:
            self.show()
            
    def rerender(self):
        """Recalculates the image of the surface.

        Returns:
            pygame.Surface: The new rendered image.
        """        
        result = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        if self._current_background_color != None:
            result.fill(self._current_background_color)
        if self._current_border_color != None and self.border_width > 0:
            border_rect = self.rect.copy()
            border_rect.topleft = (0,0)
            pygame.draw.rect(result, self._current_border_color, border_rect, self.border_width)
            
        text_surface = self.font.render(self.text, True, self._current_text_color)
        text_surface.set_alpha(colors.alpha_or_default(self._current_text_color, 255)[3])
        result.blit(text_surface, self.padding + vec(self.border_width, self.border_width))
        return result
       
    def destroy(self):
        """Kills itself, no longer being processed."""
        self.kill()
        
    def show(self):
        """Shows the popup, animating the fade in if enabled."""
        if self._show_time == None:
            self._show_time = datetime.datetime.now()
        
    def hide(self):
        """Hides and kills the popup, animating the fade out if enabled."""
        if self._hide_time == None:
            self._hide_time = datetime.datetime.now()
            
    def _fade_in_anim(self):
        anim_end = (self._show_time + datetime.timedelta(milliseconds=self.fade_in_ms))
        
        self._current_text_color = self._fade_in_color(self.text_color, colors.alpha_or_default(self.text_color, 255)[3], self._show_time, anim_end)
        if self.background_color != None:
            self._current_background_color = self._fade_in_color(self.background_color, colors.alpha_or_default(self.background_color, 255)[3], self._show_time, anim_end)
        if self.border_color != None:
            self._current_border_color = self._fade_in_color(self.border_color, colors.alpha_or_default(self.border_color, 255)[3], self._show_time, anim_end)
    
    
    def _fade_out_anim(self):
        anim_end = (self._hide_time + datetime.timedelta(milliseconds=self.fade_out_ms))
        
        self._current_text_color = self._fade_out_color(self.text_color, colors.alpha_or_default(self.text_color, 255)[3], self._hide_time, anim_end)
        if self.background_color != None:
            self._current_background_color = self._fade_out_color(self.background_color, colors.alpha_or_default(self.background_color, 255)[3], self._hide_time, anim_end)
        if self.border_color != None:
            self._current_border_color = self._fade_out_color(self.border_color, colors.alpha_or_default(self.border_color, 255)[3], self._hide_time, anim_end)
    
    def update(self, **kwargs):
        """Updates the popup. Can be called from sprite group.update()."""
        if self._show_time == None:
            return
        
        # If has time out and it's reached, start hiding
        if self.timeout_ms != None:
            _deadline = self._show_time + datetime.timedelta(milliseconds = self.timeout_ms)
            if datetime.datetime.now() > _deadline and self._hide_time == None:
                self._hide_time = datetime.datetime.now()
        
        # If has fade in animation and it's not done yet, start fading in
        if self.fade_in_ms > 0 and colors.alpha_or_default(self._current_text_color, 0)[3] < colors.alpha_or_default(self.text_color, 255)[3] and self._hide_time == None:
            self._fade_in_anim()
            
        if self._hide_time != None:
            if self.fade_out_ms > 0 and colors.alpha_or_default(self._current_text_color, 255)[3] > 0:
                self._fade_out_anim()
                if self.float_anim_distance > 0:
                    offset_y = colors.alpha_or_default(self._current_text_color, 255)[3] * self.float_anim_distance / 255
                    self.rect.top = self.start_pos.y - (self.float_anim_distance - offset_y)
            
            else:
                self.destroy()
                
                
    def draw(self, screen: pygame.Surface):
        """Draws the image on the specified surface.

        Args:
            screen (pygame.Surface): The surface to draw the popup on.
        """        
        if self._show_time == None:
            return
        
        self.image = self.rerender()
        screen.blit(self.image, self.rect)
        
    def _fade_out_color(self, color: tuple[int,int,int], start_alpha: int, start_time: datetime.datetime, end_time: datetime.datetime):
        
        now = datetime.datetime.now().timestamp()
        start = start_time.timestamp()
        end = end_time.timestamp()
        
        if start > now:
            return colors.alpha_or_default(color, start_alpha)
        
        percentage = ((now - start) / (end - start)) * 100
        percentage = math.clamp(percentage, 0, 100)
        alpha = (start_alpha*(100-percentage))/100
        alpha = math.clamp(alpha, 0, start_alpha)
        return colors.set_alpha(color, int(alpha))
    
    def _fade_in_color(self, color: tuple[int,int,int], target_alpha: int, start_time: datetime.datetime, end_time: datetime.datetime):
        
        now = datetime.datetime.now().timestamp()
        start = start_time.timestamp()
        end = end_time.timestamp()
        
        if start > now:
            return colors.alpha_or_default(color, 0)
        
        percentage = ((now - start) / (end - start)) * 100
        percentage = math.clamp(percentage, 0, 100)
        alpha = (target_alpha*percentage)/100
        alpha = math.clamp(alpha, 0, target_alpha)
        return colors.set_alpha(color, int(alpha))
        