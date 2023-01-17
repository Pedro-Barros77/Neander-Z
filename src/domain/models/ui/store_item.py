import pygame
from pygame.math import Vector2 as vec

from domain.services import game_controller, menu_controller, resources
from domain.utils import colors, constants, enums

class StoreItem:
    def __init__(self, icon_path: str, card_rect: pygame.Rect, title: str, **kwargs):
        
        #properties
        self.rect = card_rect
        self.title = title
        self.description = kwargs.pop("description", "")
        self.item_name = kwargs.pop("item_name", self.title)
        self.price = kwargs.pop("price", 0)
        self.price_text = kwargs.pop("price_text", "")
        self.count = kwargs.pop("count", 1)
        self.locked = kwargs.pop("locked", False)
        self.player_money = kwargs.pop("player_money", 0)
        self.icon_path = icon_path
        self.bullet_type: enums.BulletType = kwargs.pop("bullet_type", None)
        self.weapon_type: enums.Weapons = kwargs.pop("weapon_type", None)
        self.owned = kwargs.pop("owned", False)
        
        #control
        self.selected = False
        self.hovered = False
        self.clicked = False
        self.last_clicked = False
        
        self.on_hover:function = kwargs.pop("on_hover", self.default_on_hover)
        self.on_click:function = kwargs.pop("on_click", self.default_on_click)
        self.on_blur: function = kwargs.pop("on_blur", self.default_on_blur)
        
        self.icon = pygame.image.load(self.icon_path).convert_alpha()
        _icon_ratio = self.rect.width / self.icon.get_width()
        self.icon_scale = _icon_ratio * 0.7 * kwargs.pop("icon_scale", 1)
        self.store_icon_scale = kwargs.pop("store_icon_scale", 4)
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
        self.title_font = kwargs.pop("title_font", resources.px_font(24))
        
        
        self.price_color = kwargs.pop("price_color", colors.GREEN)
        self.price_font = kwargs.pop("price_font", resources.px_font(18))
        
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
            
    def default_on_blur(self, card = None):
        self.selected = False
        
    def default_on_click(self, card = None):
        if self.locked:
            return
        self.selected = True
        
        
    def update(self, offset: vec = vec(0,0), player_money: int = 0):
        self.player_money = player_money
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
                self.on_click(self)
        elif _was_hovered:
            self.on_hover()
            
        if not self.hovered and clicked:
            self.on_blur(self)
            
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
        
        #price
        _price_color = colors.RED if self.player_money < self.price and not self.owned else self.price_color
        _price_text = ""
        if len(self.price_text) > 0:
            _price_text = self.price_text
        elif self.owned:
            _price_text = "Purchased"
        else:
            _price_text = f'${self.price:.2f}'
        price = menu_controller.get_text_surface(_price_text, _price_color, self.price_font)
        price_rect = price.get_rect()
        price_rect.centerx = _rect.centerx
        price_rect.bottom = _rect.bottom
        if not self.locked:
            screen.blit(price, price_rect)
        
        #title
        title = menu_controller.get_text_surface(self.title, self.title_color, self.title_font)
        title_padding = vec(10,5)
        title_pos = vec(_rect.centerx - title.get_width()/2, price_rect.top - title.get_height() - title_padding.y)
        title_box = pygame.Surface(title.get_size() + title_padding*2, pygame.SRCALPHA)
        pygame.draw.rect(title_box, self.title_background_color, ((0,0),title_box.get_size()), border_radius= self.title_border_radius)
        screen.blit(title_box, title_pos - title_padding)
        screen.blit(title, title_pos)
    