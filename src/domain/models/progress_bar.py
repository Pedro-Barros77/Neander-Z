import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, math_utillity as math

class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, max_value: float, rect: pygame.Rect, **kwargs):
        super().__init__()
        
        self.max_value: float = max_value
        """The value of the bar when full filled."""
        self.value: float = self.max_value
        """The current value of the bar."""
        
        self.rect: pygame.Rect = rect
        """The size and position of the bar."""
        self.image: pygame.Surface = pygame.Surface(self.rect.size)
        """The surface of the bar, containing the result of the drawing."""
        
        self.target_value = self.max_value
        """The value of the target bar, on animation."""
        self.value_ratio = self.max_value / self.rect.width
        """The ammount of pixels to draw per value."""
        
        self.bar_color = kwargs.pop("max_color", colors.RED)
        """The color of the bar."""
        self.back_color = kwargs.pop("back_color", colors.BLACK)
        """The background color of the bar."""
        self.border_color = kwargs.pop("border_color", colors.WHITE)
        """The border color of the bar."""
        self.border_width = kwargs.pop("border_width", 2)
        """The border width of the bar."""
        self.value_anim_speed: float = kwargs.pop("value_anim_speed", 1)
        """The speed that the border value will change on animation."""
        self.anim_add_color = kwargs.pop("anim_add_color", colors.GREEN)
        """The color of the target bar on animation, when increading the value."""
        self.anim_remove_color = kwargs.pop("anim_remove_color", colors.YELLOW)
        """The color of the target bar on animation, when decreading the value."""
        self.use_animation = kwargs.pop("use_animation", True)
        """If the bar should be animated with target value bar."""
        self.hide_on_full = kwargs.pop("hide_on_full", True)
        """If the bar should be hidden when it's value is at the maximum, to prevend overflow of healthbars."""
        
        
        
    def set_rect(self, value: pygame.Rect):
        """Sets the width of the bar.

        Args:
            value (int): The new width value.
        """        
        self.rect = value
        self.image = pygame.Surface(self.rect.size)
        self.value_ratio = self.max_value / self.rect.width
    
    def draw(self, screen: pygame.Surface):
        """Draws the bar on the specified surface.

        Args:
            screen (pygame.Surface): The surface to draw the bar on.
        """        
        if self.hide_on_full and self.value == self.max_value:
            return
        screen.blit(self.image, self.rect)
        
    def update(self):
        """Updates the bar animation.
        """        
        if self.use_animation:
            self.update_bar_animation()
        else:
            self.update_bar()
        
    def remove_value(self, value: float):
        """Subtracts the value from the bar.

        Args:
            value (float): The value to be subtracted.
        """        
        if value <= 0:
            return
        if self.use_animation:
            self.target_value = math.clamp(self.target_value - value, 0, self.max_value)
        else:
            self.value = math.clamp(self.value - value, 0, self.max_value)
        
    def add_value(self, value: float):
        """Adds the value from the bar.

        Args:
            value (float): The value to be Added.
        """  
        if value <= 0:
            return
        if self.use_animation:
            self.target_value = math.clamp(self.target_value + value, 0, self.max_value)
        else:
            self.value = math.clamp(self.value + value, 0, self.max_value)
        
    def update_bar(self):
        """Updates the surface of the bar, without animating.
        """        
        self.image.fill(self.back_color)

        #current health
        pygame.draw.rect(self.image, self.bar_color, (0,0, self.value / self.value_ratio, self.rect.height))
        #current target border
        if self.border_width > 0:
            pygame.draw.rect(self.image, self.border_color, ((0,0), self.rect.size), self.border_width)
        
    def update_bar_animation(self):
        """Updates the surface of the bar, with animation.
        """        
        self.image.fill(self.back_color)
        transition_width = 0
        transition_color = colors.RED
        
        #increasing animation
        if self.value < self.target_value:
            self.value = math.clamp(self.value + self.value_anim_speed, 0, self.max_value)
            transition_width = int(abs(self.target_value - self.value) / self.value_ratio)
            transition_color = self.anim_add_color
        #decreasing animation
        if self.value > self.target_value:
            self.value = math.clamp(self.value - self.value_anim_speed, 0, self.max_value)
            transition_width = int(abs(self.target_value - self.value) / self.value_ratio)
            transition_color = self.anim_remove_color
            
        _rect = pygame.Rect(0,0, self.value / self.value_ratio, self.rect.height)
        
        if self.value < self.target_value:
            _transition_rect = pygame.Rect(_rect.right, 0, transition_width, self.rect.height)
        else:
            _transition_rect = pygame.Rect(self.target_value/self.value_ratio, 0, transition_width, self.rect.height)
            
        #current health
        pygame.draw.rect(self.image, self.bar_color, _rect)
        #current target health
        pygame.draw.rect(self.image, transition_color, _transition_rect)
        #current target border
        if self.border_width > 0:
            pygame.draw.rect(self.image, self.border_color, ((0,0), self.rect.size), self.border_width)
        
        