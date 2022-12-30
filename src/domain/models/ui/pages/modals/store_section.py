import pygame
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants, enums
from domain.models.ui.button import Button
from domain.models.ui.scrollbar import ScrollBar
from domain.models.ui.store_item import StoreItem

class Store:
    def __init__(self, player, panel_margin: vec, **kwargs):
        
        self.player = player
        self.panel_margin = panel_margin
        self.store_v_scrollbar: ScrollBar = None
        
        self.ammo_h_scrollbar: ScrollBar = None
        self.items_h_scrollbar: ScrollBar = None
        self.image: pygame.Surface = None
        self.on_return = kwargs.pop("on_return", lambda: None)
        
        self.card_size = vec(100,100)
        
        self.ammos:list[StoreItem] = [
            StoreItem(f'{constants.IMAGES_PATH}ui\\pistol_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Pistol Ammo", "+10"),
            StoreItem(f'{constants.IMAGES_PATH}ui\\shotgun_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Shotgun Ammo", "+5"),
            StoreItem(f'{constants.IMAGES_PATH}ui\\rifle_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rifle Ammo", "+30"),
            StoreItem(f'{constants.IMAGES_PATH}ui\\sniper_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Sniper Ammo", "+5")
        ]
        
        self.items:list[StoreItem] = [
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", "+10", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", "+5", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", "+30", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", "+5", locked = True)
        ]
        
        
        self.ammo_panel_buttons = [
                Button((0,0), f'{constants.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_forward(100)),
                Button((0,0), f'{constants.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_backward(100))
            ]
        self.items_panel_buttons = [
                Button((0,0), f'{constants.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_forward(100)),
                Button((0,0), f'{constants.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_backward(100))
            ]
        
        self.buttons: list[Button] = [
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{constants.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = self.on_return)
            ]
        self.buttons.extend([*self.ammo_panel_buttons, *self.items_panel_buttons])

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def update(self, **kwargs):
        events = kwargs.pop("events", [])
        
        for e in events:
            if self.store_v_scrollbar != None:
                self.store_v_scrollbar.event_handler(e)
                self.store_v_scrollbar.update()
            if self.ammo_h_scrollbar != None:
                self.ammo_h_scrollbar.event_handler(e, self.store_v_scrollbar.scroll_offset)
                self.ammo_h_scrollbar.update()
            if self.items_h_scrollbar != None:
                self.items_h_scrollbar.event_handler(e, self.store_v_scrollbar.scroll_offset)
                self.items_h_scrollbar.update()
                
        for card in [*self.ammos, *self.items]:
            card.update(self.panel_margin/2)

        for b in self.buttons:
            b.update()
            
    def get_panel(self,image_rect: pygame.Rect, height: float, title_text: str, cards: list[StoreItem], scroll: ScrollBar = None):
        _panel_margin = vec(40,5)
        _padding = vec(50,10)
        _items_margin_x = cards[0].rect.width + 80
        _offset_x = vec(0,0)
        _offset_y = vec(0,0)
        
        if scroll != None:
            _offset_x += scroll.scroll_offset
        if self.store_v_scrollbar != None:
            _offset_y += self.store_v_scrollbar.scroll_offset
        
        title = menu_controller.get_text_surface(title_text, colors.WHITE, self.font(50))
        title_rect = title.get_rect()
        title_rect.topleft += _offset_y
        
        panel = pygame.Surface((image_rect.width - _panel_margin.x*3, self.card_size.y + _panel_margin.y*2 + _padding.y*2 + title_rect.height), pygame.SRCALPHA)
        panel_rect = panel.get_rect()
        panel_rect.left = _panel_margin.x
        panel_rect.top = height + title_rect.height + _offset_y.y
        _scroll_rect = pygame.Rect((0,title_rect.height),panel_rect.size - vec(0,title_rect.height))
        pygame.draw.rect(panel, colors.LIGHT_GRAY, _scroll_rect, 2)
        
        panel.blit(title, (0,0))
        
        for i, item in enumerate(cards):
            _item_rect = item.rect.copy()
            _item_rect.bottom = panel_rect.bottom - _padding.y
            item.set_pos(vec(_panel_margin.x + _padding.x + (i * _items_margin_x), _item_rect.top) + _offset_x)
            item.draw(panel, vec(-_panel_margin.x, -height - title_rect.height - _offset_y.y))
            
        _scroll_rect.top = panel_rect.top + title_rect.height
        return panel, panel_rect, _scroll_rect
        
        
                
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        if self.image == None:
            self.image = pygame.Surface(screen_rect.size - self.panel_margin, pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        image_rect = self.image.get_rect()
        image_rect.topleft = self.panel_margin/2
        
        #title
        store_title = menu_controller.get_text_surface("Store", colors.WHITE, self.font(80))     

        _panels_distance = 250
        
        #panel ammo
        ammo_panel, ammo_panel_rect, ammo_panel_scroll_rect = self.get_panel(image_rect, store_title.get_height(),"Ammunition", self.ammos, self.ammo_h_scrollbar)
        self.ammo_panel_buttons[0].rect.centery = self.ammos[0].rect.centery + self.panel_margin.y/2
        self.ammo_panel_buttons[1].rect.centery = self.ammos[0].rect.centery + self.panel_margin.y/2
        self.ammo_panel_buttons[0].rect.right = ammo_panel_rect.left + image_rect.left - 5
        self.ammo_panel_buttons[1].rect.left = ammo_panel_rect.right + image_rect.left + 5
        
        #panel items
        items_panel, items_panel_rect, items_panel_scroll_rect = self.get_panel(image_rect, store_title.get_height() + _panels_distance,"Items", self.items, self.items_h_scrollbar)
        self.items_panel_buttons[0].rect.centery = self.items[0].rect.centery + self.panel_margin.y/2
        self.items_panel_buttons[1].rect.centery = self.items[0].rect.centery + self.panel_margin.y/2
        self.items_panel_buttons[0].rect.right = items_panel_rect.left + image_rect.left - 5
        self.items_panel_buttons[1].rect.left = items_panel_rect.right + image_rect.left + 5
        
        if self.ammo_h_scrollbar == None:
            self.ammo_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec(self.card_size.x * len(self.ammos)*2.1,1), pygame.Rect((ammo_panel_rect.left + self.panel_margin.x/2, ammo_panel_scroll_rect.bottom + 27), (ammo_panel_scroll_rect.width, 20)), focused = False, auto_focus = False)
            
        if self.items_h_scrollbar == None:
            self.items_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec(self.card_size.x * len(self.items)*2.1,1), pygame.Rect((items_panel_rect.left + self.panel_margin.x/2, items_panel_scroll_rect.bottom + 27), (items_panel_scroll_rect.width, 20)), focused = False, auto_focus = False)
        
        if self.store_v_scrollbar == None:
            self.store_v_scrollbar = ScrollBar(enums.Orientation.VERTICAL, vec(1,(screen_rect.height-self.panel_margin.y) *2), pygame.Rect((screen_rect.width - self.panel_margin.x, self.panel_margin.y + store_title.get_height()), (20,screen_rect.height - self.panel_margin.y*2 - (store_title.get_height()))))
            
            
            
        #   --drawing--
        
        #panels
        self.image.blit(ammo_panel, ammo_panel_rect)
        self.image.blit(items_panel, items_panel_rect)
        
        #scroll bars
        self.ammo_h_scrollbar.draw(self.image, self.store_v_scrollbar.scroll_offset - self.panel_margin/2)
        self.items_h_scrollbar.draw(self.image, self.store_v_scrollbar.scroll_offset - self.panel_margin/2)
        self.store_v_scrollbar.draw(self.image, - self.panel_margin/2)
        
        #buttons
        for b in self.buttons:
            b.draw(self.image, -self.panel_margin/2)

        #store header
        pygame.draw.rect(self.image, colors.BLACK, ((0,0), (image_rect.width, store_title.get_height() + 10)))
        self.image.blit(store_title, (image_rect.width/2 - store_title.get_width()/2, 10))
        self.buttons[0].draw(self.image, -self.panel_margin/2)
            
        screen.blit(self.image, image_rect)
       
            