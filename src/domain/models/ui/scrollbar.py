import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums

class ScrollBar(object):
    def __init__(self, orientation: enums.Orientation, content_size: vec, scroll_rect: pygame.Rect, **kwargs):
        
        #dimensions
        self.orientation = orientation
        """If the bar will scroll horizontally or vertically."""
        self.content_size = content_size
        """The width and height of the content to be scrolled."""

        #properties
        self.focused = kwargs.pop("focused", True)
        """If the scrollbar is focused and should respond to input."""
        self.auto_focus = kwargs.pop("auto_focus", True)
        """If the scrollbar is focused on click."""
        self.visible = kwargs.pop("visible", True)
        """If the scrollbar is visible on the screen."""
        self.step = kwargs.pop("step", 30)
        """How much to scroll per click."""
        self.wheel_step_multiplier = kwargs.pop("wheel_step_multiplier", 2)
        """The step multiplier for the mouse scroll wheel."""
        
        #control
        self.scroll_offset: vec = vec(0,0)
        """The offset of the scrollbar. Add it to the position of the elements to be moved."""
        self.scroll_change:vec = vec(0,0)
        """How much the scroll position has changed since last frame."""
        self.holding_bar = False
        """If the bar (slider) is currently being held by the cursor."""
        self.mouse_diff: vec = vec(0,0)
        """The difference of the distance between the cursor position and the bar position."""
        self.on_focus: function = lambda: None
        """Function to be called when the scrollbar gets focused."""
        self.on_unfocus: function = lambda: None
        """Function to be called when the scrollbar gets unfocused."""
        
        #rail style
        self.rail_color = kwargs.pop("background_color", colors.WHITE)
        """The background color of the rail (scroll box) of the scrollbar."""
        self.rail_border_color = kwargs.pop("rail_border_color", colors.SCROLL_GRAY)
        """The border color of the rail (scroll box) of the scrollbar."""
        self.rail_border_width = kwargs.pop("rail_border_width", 1)
        """The border width of the rail (scroll box) of the scrollbar."""
        self.rail_border_radius = kwargs.pop("rail_border_radius", 8)
        """The border radius of the rail (scroll box) of the scrollbar."""
        
        #bar style
        self.bar_color = kwargs.pop("rail_border_color", colors.SCROLL_GRAY)
        """The color of the bar (slider) of the scrollbar."""
        self.bar_border_color = colors.alpha_or_default(kwargs.pop("rail_border_color", colors.SCROLL_GRAY), 0)
        """The border color of the bar (slider) of the scrollbar."""
        self.bar_border_width = kwargs.pop("bar_border_width", 0)
        """The border width of the bar (slider) of the scrollbar."""
        self.bar_width_scale = kwargs.pop("bar_width_scale", 0.6)
        """The width scale of the bar (slider) of the scrollbar. How thick it is in proportion with the rail."""
        
        #arrows style
        self.arrows_color = kwargs.pop("arrows_color", colors.SCROLL_GRAY)
        """The color of the arrows (buttons) of the scrollbar."""
        self.arrows_scale = kwargs.pop("arrows_scale", 0.4)
        """The scale of the arrows in proportion with the buttons."""
        self.arrows_length_scale = kwargs.pop("arrows_length_scale", 0.8)
        """The length scale of the arrows in proportion with their width. How the triangle is longer than wider."""
        
        
        #rail
        self.rail_rect: pygame.Rect = scroll_rect
        """The rect of the rail (background) of the scrollbar."""
        self.rail: pygame.Surface = pygame.Surface(self.rail_rect.size)
        """The the rail (background) surface of the scrollbar."""
        
        #bar
        self.bar_rect: pygame.Rect = None
        """The rect of the bar (slider) of the scrollbar."""
        self.bar: pygame.Surface = None
        """The the bar (slider) surface of the scrollbar."""

        #arrow1
        self.arrow1_rect: pygame.Rect = None
        """The rect of the left/top arrow of the scrollbar."""
        self.arrow1: pygame.Surface = None
        """The the left/top arrow surface of the scrollbar."""

        #arrow2
        self.arrow2_rect: pygame.Rect = None
        """The rect of the right/bottom arrow of the scrollbar."""
        self.arrow2: pygame.Surface = None
        """The the right/bottom arrow surface of the scrollbar."""
        
        if self.orientation == enums.Orientation.VERTICAL:
            #arrow1
            self.arrow1_rect = self.rail_rect.copy()
            self.arrow1_rect.width = self.rail_rect.width
            self.arrow1_rect.height = self.arrow1_rect.width
            self.arrow1_rect.centerx = self.rail_rect.centerx
            self.arrow1_rect.top = self.rail_rect.top
            self.arrow1 = pygame.Surface(self.arrow1_rect.size, pygame.SRCALPHA)
            
            #arrow2
            self.arrow2_rect = self.arrow1_rect.copy()
            self.arrow2_rect.bottom = self.rail_rect.bottom
            self.arrow2 = pygame.Surface(self.arrow2_rect.size, pygame.SRCALPHA)
            
            #bar
            self.bar_rect = self.rail_rect.copy()
            self.bar_rect.width = self.rail_rect.width * self.bar_width_scale 
            self.bar_rect.height = int((self.rail_rect.height - self.arrow1_rect.height*2) / (self.content_size.y / (self.rail_rect.height * 1.0)))
            self.bar_rect.centerx = self.rail_rect.centerx
            self.bar = pygame.Surface(self.bar_rect.size, pygame.SRCALPHA)

        elif self.orientation == enums.Orientation.HORIZONTAL:
            #arrow1
            self.arrow1_rect = self.rail_rect.copy()
            self.arrow1_rect.height = self.rail_rect.height * 0.8
            self.arrow1_rect.width = self.arrow1_rect.height
            self.arrow1_rect.centery = self.rail_rect.centery
            self.arrow1_rect.left = self.rail_rect.left
            self.arrow1 = pygame.Surface(self.arrow1_rect.size, pygame.SRCALPHA)
            
            #arrow2
            self.arrow2_rect = self.arrow1_rect.copy()
            self.arrow2_rect.right = self.rail_rect.right
            self.arrow2 = pygame.Surface(self.arrow2_rect.size, pygame.SRCALPHA)
            
            #bar
            self.bar_rect = self.rail_rect.copy()
            self.bar_rect.height = self.rail_rect.height * self.bar_width_scale 
            self.bar_rect.width = int((self.rail_rect.width - self.arrow1_rect.width*2) / (self.content_size.x / (self.rail_rect.width * 1.0)))
            self.bar_rect.centery = self.rail_rect.centery
            self.bar = pygame.Surface(self.bar_rect.size, pygame.SRCALPHA)
        
    def focus(self):
        self.focused = True
        self.on_focus()
        
    def unfocus(self):
        self.focused = False
        self.on_unfocus()
        
    def update_vertical(self):
        if self.scroll_offset.y > 0:
            self.scroll_offset.y = 0
        elif (self.scroll_offset.y + self.content_size.y) < self.rail_rect.height:
            self.scroll_offset.y = self.rail_rect.height - self.content_size.y
            
        height_diff = self.content_size.y - self.rail_rect.height
        
        scroll_length = self.rail_rect.height - self.bar_rect.height - self.arrow1_rect.height*2
        bar_half_lenght = self.bar_rect.height / 2 + self.arrow1_rect.height
        
        if self.holding_bar:
            pos = pygame.mouse.get_pos()
            self.bar_rect.y = pos[1] - self.mouse_diff.y
            if self.bar_rect.top < self.arrow1_rect.height + self.rail_rect.top:
                self.bar_rect.top = self.arrow1_rect.height + self.rail_rect.top
            elif self.bar_rect.bottom > (self.rail_rect.height - self.arrow1_rect.height + self.rail_rect.top):
                self.bar_rect.bottom = self.rail_rect.height - self.arrow1_rect.height + self.rail_rect.top
            
            self.scroll_offset.y = int(height_diff / (scroll_length * 1.0) * (self.bar_rect.centery - bar_half_lenght - self.rail_rect.top) * -1)
        else:
            self.bar_rect.centery =  scroll_length / (height_diff * 1.0) * (self.scroll_offset.y * -1) + bar_half_lenght + self.rail_rect.top

    def update_horizontal(self):
        if self.scroll_offset.x > 0:
            self.scroll_offset.x = 0
        elif (self.scroll_offset.x + self.content_size.x) < self.rail_rect.width:
            self.scroll_offset.x = self.rail_rect.width - self.content_size.x
            
        width_diff = self.content_size.x - self.rail_rect.width
        
        scroll_length = self.rail_rect.width - self.bar_rect.width - self.arrow1_rect.width*2
        bar_half_lenght = self.bar_rect.width / 2 + self.arrow1_rect.width
        
        if self.holding_bar:
            pos = pygame.mouse.get_pos()
            self.bar_rect.x = pos[0] - self.mouse_diff.x
            if self.bar_rect.left < self.arrow1_rect.width + self.rail_rect.left:
                self.bar_rect.left = self.arrow1_rect.width + self.rail_rect.left
            elif self.bar_rect.right > (self.rail_rect.width - self.arrow1_rect.width + self.rail_rect.left):
                self.bar_rect.right = self.rail_rect.width - self.arrow1_rect.width + self.rail_rect.left
            
            self.scroll_offset.x = int(width_diff / (scroll_length * 1.0) * (self.bar_rect.centerx - bar_half_lenght - self.rail_rect.left) * -1)
        else:
            self.bar_rect.centerx =  scroll_length / (width_diff * 1.0) * (self.scroll_offset.x * -1) + bar_half_lenght + self.rail_rect.left
        
    def update(self):
        
        self.scroll_offset += self.scroll_change
        
        if self.orientation == enums.Orientation.VERTICAL:
            self.update_vertical()
             
        elif self.orientation == enums.Orientation.HORIZONTAL:
            self.update_horizontal()
        
        self.scroll_change = vec(0,0)
        
    def move_forward(self, step = None):
        _step = step if step != None else self.step
        
        if self.orientation == enums.Orientation.VERTICAL:
            self.scroll_change.y = _step
        else:
            self.scroll_change.x = _step
            
    def move_backward(self, step = None):
        _step = step if step != None else self.step
        
        if self.orientation == enums.Orientation.VERTICAL:
            self.scroll_change.y = -_step
        else:
            self.scroll_change.x = -_step
            
        
    def event_handler(self,event, offset: vec = vec(0,0)):
        is_vertical = self.orientation == enums.Orientation.VERTICAL
        i = 1 if is_vertical else 0
        _rect = self.bar_rect.copy()
        _arrow1_rect = self.arrow1_rect.copy()
        _arrow2_rect = self.arrow2_rect.copy()
        _rect.topleft += offset
        _arrow1_rect.topleft += offset
        _arrow2_rect.topleft += offset
        
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            
            
            if _rect.collidepoint(pos) and self.visible:
                if self.auto_focus:
                    self.focus()
                if is_vertical:
                    self.mouse_diff.y = pos[1] - self.bar_rect.y
                else:
                    self.mouse_diff.x = pos[0] - self.bar_rect.x
                self.holding_bar = True
            elif _arrow1_rect.collidepoint(pos):
                if self.auto_focus:
                    self.focus()
                self.scroll_change[i] = self.step
            elif _arrow2_rect.collidepoint(pos):
                if self.auto_focus:
                    self.focus()
                self.scroll_change[i] = -self.step
                
        if event.type == pygame.MOUSEBUTTONUP:
            # self.scroll_change[i] = 0
            self.holding_bar = False
            
        if event.type == pygame.MOUSEWHEEL and self.focused:
            self.scroll_change[i] = self.step * event.y * self.wheel_step_multiplier
        
        
        if event.type == pygame.KEYDOWN and self.focused:
            if is_vertical:
                if event.key == pygame.K_UP:
                    self.scroll_change.y = self.step
                elif event.key == pygame.K_DOWN:
                    self.scroll_change.y = -self.step
            else:
                if event.key == pygame.K_LEFT:
                    self.scroll_change.x = self.step
                elif event.key == pygame.K_RIGHT:
                    self.scroll_change.x = -self.step
                    
            if event.type == pygame.KEYUP and self.focused:
                if (is_vertical and event.key == pygame.K_UP or event.key == pygame.K_DOWN) or (not is_vertical and event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                    self.scroll_change[i] = 0
                
    def draw(self,screen: pygame.Surface, offset:vec = vec(0,0)):
        if not self.visible:
            return
        self.draw_arrows()
        is_vertical = self.orientation == enums.Orientation.VERTICAL
        
        #rail background
        pygame.draw.rect(screen, self.rail_color, pygame.Rect(self.rail_rect.topleft + offset,self.rail_rect.size), border_radius=self.rail_border_radius)
        #rail border
        pygame.draw.rect(screen, self.rail_border_color, pygame.Rect(self.rail_rect.topleft + offset,self.rail_rect.size), self.rail_border_width, self.rail_border_radius)
        #bar
        pygame.draw.rect(screen,self.bar_color, pygame.Rect(self.bar_rect.topleft + offset,self.bar_rect.size), border_radius=self.rail_border_radius)
        #bar border
        pygame.draw.rect(screen,self.bar_color, pygame.Rect(self.bar_rect.topleft + offset,self.bar_rect.size), self.bar_border_width, self.rail_border_radius)
        
        screen.blit(self.arrow1, pygame.Rect(self.arrow1_rect.topleft + offset,self.arrow1_rect.size))
        screen.blit(self.arrow2, pygame.Rect(self.arrow2_rect.topleft + offset,self.arrow2_rect.size))
        
    def draw_arrows(self):
        if self.orientation == enums.Orientation.VERTICAL:
            _size = vec(self.arrow1_rect.width * self.arrows_scale, (self.arrow1_rect.height * self.arrows_scale) * self.arrows_length_scale)
            _offset = vec(self.arrow1_rect.size) - _size
            #top arrow
            pygame.draw.polygon(self.arrow1, self.arrows_color, (
                    (_size.x/2, 0) + _offset/2,
                    (_size.x, _size.y) + _offset/2,
                    (0, _size.y) + _offset/2
                ))
            #bottom arrow
            pygame.draw.polygon(self.arrow2, self.arrows_color, (
                    (_size.x/2, _size.y) + _offset/2,
                    (_size.x, 0) + _offset/2,
                    (0, 0) + _offset/2
                ))
        elif self.orientation == enums.Orientation.HORIZONTAL:
            _size = vec((self.arrow1_rect.width * self.arrows_scale) * self.arrows_length_scale, self.arrow1_rect.height * self.arrows_scale)
            _offset = vec(self.arrow1_rect.size) - _size
            #top arrow
            pygame.draw.polygon(self.arrow1, self.arrows_color, (
                    (0, _size.y/2) + _offset/2,
                    (_size.x, _size.y) + _offset/2,
                    (_size.x, 0) + _offset/2
                ))
            #bottom arrow
            pygame.draw.polygon(self.arrow2, self.arrows_color, (
                    (_size.x, _size.y/2) + _offset/2,
                    (0, _size.y) + _offset/2,
                    (0, 0) + _offset/2
                ))