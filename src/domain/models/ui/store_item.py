import pygame
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller
from domain.utils import colors, constants

class StoreItem:
    def __init__(self, icon_path: str, card_rect: pygame.Rect, title: str, button_text: str, **kwargs):
        
        #properties
        self.rect = card_rect
        self.title = title
        self.button_text = button_text
        self.description = kwargs.pop("description", "")
        self.item_name = kwargs.pop("item_name", self.title)
        self.price = kwargs.pop("price", 0)
        self.count = kwargs.pop("count", 1)
        
        #control
        self.selected = False
        self.hovered = False
        self.clicked = False
        self.last_clicked = False
        
        self.on_hover:function = kwargs.pop("on_hover", self.default_on_hover)
        self.on_click:function = kwargs.pop("on_click", self.default_on_click)
        
        self.icon = pygame.image.load(icon_path)
        _icon_ratio = self.rect.width / self.icon.get_width()
        self.icon_scale = kwargs.pop("image_scale", _icon_ratio * 0.7)
        self.icon = game_controller.scale_image(self.icon, self.icon_scale)
        self.icon_rect = self.icon.get_rect()
        self.icon_rect.centerx = self.rect.centerx
        self.icon_rect.top = self.rect.top - (self.icon_rect.height * 0.3)
        
        self.btn_rect = self.rect.copy()
        
        #style
        self.card_background_color = kwargs.pop("card_background_color", colors.DARK_GRAY)
        self.card_border_color = kwargs.pop("card_border_color", colors.LIGHT_GRAY)
        self.card_border_width = kwargs.pop("card_border_width", 1)
        self.card_border_radius = kwargs.pop("card_border_radius", 5)
        
        self.title_color = kwargs.pop("title_color", colors.WHITE)
        self.title_background_color = kwargs.pop("title_background_color", colors.set_alpha(colors.BLACK, 150))
        self.title_border_radius = kwargs.pop("title_border_radius", 10)
        self.title_font = kwargs.pop("title_font", pygame.font.Font(constants.PIXEL_FONT, 30))
        
        self.btn_text_color = kwargs.pop("btn_text_color", colors.WHITE)
        self.btn_background_color = kwargs.pop("btn_background_color", colors.GREEN)
        self.btn_border_color = kwargs.pop("btn_border_color", colors.WHITE)
        self.btn_border_radius = kwargs.pop("btn_border_radius", 8)
        self.btn_border_width = kwargs.pop("btn_border_width", 1)
        self.btn_font = kwargs.pop("btn_font", pygame.font.Font(constants.PIXEL_FONT, 25))

        self.card_selected_border_color = kwargs.pop("card_selected_border_color", colors.GREEN)
        self.selected_scale = kwargs.pop("selected_scale", 1.2)
        self.card_hovered_border_color = kwargs.pop("card_hovered_border_color", colors.WHITE)

    def set_pos(self, pos: vec):
        self.rect.topleft = pos
        self.icon_rect.centerx = self.rect.centerx
        self.icon_rect.top = self.rect.top - (self.icon_rect.height * 0.3)
        

    def default_on_hover(self):
        _brightness = 30
        
        if self.hovered: #hover in
            self.card_background_color = colors.add(self.card_background_color, (_brightness, _brightness, _brightness))
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: #hover out
            self.card_background_color = colors.add(self.card_background_color, (-_brightness, -_brightness, -_brightness))
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
    def default_on_click(self):
        # print('clicked ' + self.title)
        self.selected = True
        
        
    def update(self, offset: vec = vec(0,0)):
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0] == 1
        
        _was_hovered = self.hovered
        _rect = self.rect.copy()
        _rect.topleft += offset
        self.hovered = _rect.collidepoint(mouse_pos)
        if self.hovered:
            if not _was_hovered:
                self.on_hover()
            if clicked and not self.clicked and not self.last_clicked:
                self.clicked = True
                self.on_click()
        elif _was_hovered:
            self.on_hover()
            
        if not self.hovered and clicked:
            self.selected = False
            
        if not clicked:
            self.clicked = False
        
        self.last_clicked = clicked
    
    
    
    def draw(self, screen: pygame.Surface, offset: vec = vec(0,0)):
        #card bg
        
        _rect = self.rect.copy()
        if self.selected:
            _rect.size = vec(_rect.size) * self.selected_scale
            _rect.center = self.rect.center
        _rect.topleft += offset
        pygame.draw.rect(screen, self.card_background_color, _rect, border_radius=self.card_border_radius)
        #card border
        border_color = None
        if self.selected:
            border_color = self.card_selected_border_color
        elif self.hovered:
            border_color = self.card_hovered_border_color
        else:
            border_color = self.card_border_color
            
        pygame.draw.rect(screen, border_color, _rect, self.card_border_width, self.card_border_radius)
        #icon
        _icon = self.icon
        _icon_rect = self.icon_rect.copy()
        if self.selected:
            _icon = game_controller.scale_image(self.icon, self.selected_scale)
            _icon_rect = _icon.get_rect()
            _icon_rect.center = self.icon_rect.center
        _icon_rect.topleft += offset
        screen.blit(_icon, _icon_rect)
        
        #title
        title = menu_controller.get_text_surface(self.title, self.title_color, self.title_font)
        title_padding = vec(10,5)
        title_pos = vec(_rect.centerx - title.get_width()/2, _rect.bottom - title.get_height() - title_padding.y)
        title_box = pygame.Surface(title.get_size() + title_padding*2, pygame.SRCALPHA)
        pygame.draw.rect(title_box, self.title_background_color, ((0,0),title_box.get_size()), border_radius= self.title_border_radius)
        screen.blit(title_box, title_pos - title_padding)
        screen.blit(title, title_pos)

        # btn_padding = vec(5,5)
        # btn_text = menu_controller.get_text_surface(self.button_text, self.btn_text_color, self.btn_font)
        # self.btn_rect.width = btn_text.get_width() + btn_padding.x*2
        # self.btn_rect.height = btn_text.get_height() + btn_padding.y*2
        # self.btn_rect.centerx = self.rect.centerx
        # self.btn_rect.centery = self.rect.bottom
        # #button bg
        # pygame.draw.rect(screen, self.btn_background_color, self.btn_rect, border_radius=self.btn_border_radius)
        # #button border
        # pygame.draw.rect(screen, self.btn_border_color, self.btn_rect, self.btn_border_width, self.btn_border_radius)
        # #button text
        # screen.blit(btn_text, vec(self.btn_rect.centerx - btn_text.get_width()/2, self.btn_rect.centery - btn_text.get_height()/2))
        
        # screen.blit(self.image, self.rect)