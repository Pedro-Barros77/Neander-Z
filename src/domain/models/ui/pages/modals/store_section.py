import pygame
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants, enums
from domain.models.ui.button import Button
from domain.models.ui.popup_text import Popup
from domain.models.ui.scrollbar import ScrollBar
from domain.models.ui.store_item import StoreItem

class Store:
    def __init__(self, player: Player, panel_margin: vec, **kwargs):
        
        self.player = player
        self.panel_margin = panel_margin
        self.store_v_scrollbar: ScrollBar = None
        
        self.ammo_h_scrollbar: ScrollBar = None
        self.items_h_scrollbar: ScrollBar = None
        self.weapons_h_scrollbar: ScrollBar = None
        self.image: pygame.Surface = None
        self.on_return = kwargs.pop("on_return", lambda: None)
        
        self.money_rect: pygame.Rect = None
        
        self.selected_card: StoreItem = None
        self.card_size = vec(100,100)
        
        _cards_descriptions = {
            enums.BulletType.PISTOL: "It's ammo, for a pistol.\nYou put it in a pistol and fire...\nWhat else shoud it be?",
            enums.BulletType.SHOTGUN: "Why shoot one bullet if you can\nshoot 12 at once?",
            enums.BulletType.ASSAULT_RIFLE: "Auto fire goes brrrrrrrrr",
            enums.BulletType.SNIPER: "They won't know what hit'em!",
            enums.BulletType.ROCKET: "Booooom!",
        }
        
        def _select_card(card: StoreItem):
            card.default_on_click()
            self.selected_card = card
        
        def _unselect_card(card: StoreItem):
            btns_hovered = [b for b in self.buttons if b.hovered]
            scroll_bars_held = [s for s in [self.ammo_h_scrollbar, self.items_h_scrollbar, self.weapons_h_scrollbar, self.store_v_scrollbar] if s.holding_bar]
            
            if len(btns_hovered) > 0 or len(scroll_bars_held) > 0:
                return
            
            
            card.default_on_blur()
            if self.selected_card != None and self.selected_card.item_name == card.item_name:
                self.selected_card = None
        
        cards_dict = {
            "on_click": _select_card,
            "on_blur": _unselect_card
        }    
        
        self.ammos:list[StoreItem] = [
            StoreItem(f'{constants.IMAGES_PATH}ui\\pistol_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Pistol Ammo", item_name = "pistol_ammo", price = 20, count = 10, bullet_type = enums.BulletType.PISTOL, **cards_dict),
            StoreItem(f'{constants.IMAGES_PATH}ui\\shotgun_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Shotgun Ammo", item_name = "shotgun_ammo", price = 30, count = 5, bullet_type = enums.BulletType.SHOTGUN, **cards_dict),
            StoreItem(f'{constants.IMAGES_PATH}ui\\rifle_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rifle Ammo", item_name = "rifle_ammo", price = 45, count = 30, bullet_type = enums.BulletType.ASSAULT_RIFLE, **cards_dict),
            StoreItem(f'{constants.IMAGES_PATH}ui\\sniper_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Sniper Ammo", item_name = "sniper_ammo", price = 40, count =5, bullet_type = enums.BulletType.SNIPER, **cards_dict),
            StoreItem(f'{constants.IMAGES_PATH}ui\\rocket_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rocket Ammo", item_name = "rocket_ammo", price = 135, count =1, bullet_type = enums.BulletType.ROCKET, **cards_dict)
        ]
        
        self.items:list[StoreItem] = [
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True)
        ]
        
        self.weapons:list[StoreItem] = [
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{constants.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True)
        ]
        
        self.cards_list = [*self.ammos, *self.items, *self.weapons]
        for c in self.cards_list:
            c.description = _cards_descriptions.pop(c.bullet_type, "")
            
        
        
        self.ammo_panel_buttons = [
                Button((0,0), f'{constants.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_forward(100)),
                Button((0,0), f'{constants.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_backward(100))
            ]
        
        self.items_panel_buttons = [
                Button((0,0), f'{constants.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_forward(100)),
                Button((0,0), f'{constants.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_backward(100))
            ]
        
        self.weapons_panel_buttons = [
                Button((0,0), f'{constants.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.weapons_h_scrollbar.move_forward(100)),
                Button((0,0), f'{constants.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.weapons_h_scrollbar.move_backward(100))
            ]
        
        self.buttons: list[Button] = [
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{constants.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = self.on_return),
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{constants.IMAGES_PATH}ui\\btn_small_green.png', text_font = self.font(20), text_color = colors.BLACK, scale=1.4, visible = False, hover_scale=1, on_click = self.process_purchase)
            ]
        
        self.buttons.extend([*self.ammo_panel_buttons, *self.items_panel_buttons, *self.weapons_panel_buttons])

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def update(self, **kwargs):
        events = kwargs.pop("events", [])
        
        if self.selected_card != None:
            self.buttons[1].show()
        else:
            self.buttons[1].hide()
        
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
            if self.weapons_h_scrollbar != None:
                self.weapons_h_scrollbar.event_handler(e, self.store_v_scrollbar.scroll_offset)
                self.weapons_h_scrollbar.update()
                
        for b in self.buttons:
            b.update()
            
        if self.selected_card != None:
            btn_buy = self.buttons[1]
            btn_buy.set_text(f'Buy +{self.selected_card.count}')
            btn_buy_enabled = self.player.money >= self.selected_card.price
            if btn_buy_enabled and not btn_buy.enabled:
                btn_buy.enable(True)
            elif not btn_buy_enabled and btn_buy.enabled:
                btn_buy.enable(False)

        for card in self.cards_list:
            card.update(self.panel_margin/2, self.player.money)

            
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
        txt_store_title = menu_controller.get_text_surface("Store", colors.WHITE, self.font(80))
        txt_store_title_rect = txt_store_title.get_rect()
        txt_store_title_rect.topleft = vec(self.buttons[0].rect.right, 10)

        _item_description_size = vec(400,150)
        _panels_distance = 250
        
        #panel ammo
        ammo_panel, ammo_panel_rect, ammo_panel_scroll_rect = self.get_panel(image_rect, txt_store_title_rect.height,"Ammunition", self.ammos, self.ammo_h_scrollbar)
        self.ammo_panel_buttons[0].rect.centery = self.ammos[0].rect.centery + self.panel_margin.y/2
        self.ammo_panel_buttons[1].rect.centery = self.ammos[0].rect.centery + self.panel_margin.y/2
        self.ammo_panel_buttons[0].rect.right = ammo_panel_rect.left + image_rect.left - 5
        self.ammo_panel_buttons[1].rect.left = ammo_panel_rect.right + image_rect.left + 5
        
        #panel items
        items_panel, items_panel_rect, items_panel_scroll_rect = self.get_panel(image_rect, txt_store_title_rect.height + _panels_distance,"Items", self.items, self.items_h_scrollbar)
        self.items_panel_buttons[0].rect.centery = self.items[0].rect.centery + self.panel_margin.y/2
        self.items_panel_buttons[1].rect.centery = self.items[0].rect.centery + self.panel_margin.y/2
        self.items_panel_buttons[0].rect.right = items_panel_rect.left + image_rect.left - 5
        self.items_panel_buttons[1].rect.left = items_panel_rect.right + image_rect.left + 5
        
        #panel weapons
        weapons_panel, weapons_panel_rect, weapons_panel_scroll_rect = self.get_panel(image_rect, txt_store_title_rect.height + _panels_distance*2,"Weapons", self.weapons, self.weapons_h_scrollbar)
        self.weapons_panel_buttons[0].rect.centery = self.weapons[0].rect.centery + self.panel_margin.y/2
        self.weapons_panel_buttons[1].rect.centery = self.weapons[0].rect.centery + self.panel_margin.y/2
        self.weapons_panel_buttons[0].rect.right = weapons_panel_rect.left + image_rect.left - 5
        self.weapons_panel_buttons[1].rect.left = weapons_panel_rect.right + image_rect.left + 5
        
        if self.ammo_h_scrollbar == None:
            self.ammo_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec(self.card_size.x * len(self.ammos)*2.1,1), pygame.Rect((ammo_panel_rect.left + self.panel_margin.x/2, ammo_panel_scroll_rect.bottom + 27), (ammo_panel_scroll_rect.width, 20)), focused = False, auto_focus = False)
            
        if self.items_h_scrollbar == None:
            self.items_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec(self.card_size.x * len(self.items)*2.1,1), pygame.Rect((items_panel_rect.left + self.panel_margin.x/2, items_panel_scroll_rect.bottom + 27), (items_panel_scroll_rect.width, 20)), focused = False, auto_focus = False)
        
        if self.weapons_h_scrollbar == None:
            self.weapons_h_scrollbar = ScrollBar(enums.Orientation.HORIZONTAL, vec(self.card_size.x * len(self.weapons)*2.1,1), pygame.Rect((weapons_panel_rect.left + self.panel_margin.x/2, weapons_panel_scroll_rect.bottom + 27), (weapons_panel_scroll_rect.width, 20)), focused = False, auto_focus = False)
        
        if self.store_v_scrollbar == None:
            self.store_v_scrollbar = ScrollBar(enums.Orientation.VERTICAL, vec(1,(screen_rect.height-self.panel_margin.y) *2), pygame.Rect((screen_rect.width - self.panel_margin.x, self.panel_margin.y + _item_description_size.y), (20,screen_rect.height - self.panel_margin.y*2 - _item_description_size.y)))
            
            
        p1_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png'), 2.5)
        p1_icon_rect = p1_icon.get_rect()
        p1_icon_rect.left = txt_store_title_rect.right + 30
        p1_icon_rect.centery = txt_store_title_rect.centery

        txt_money = menu_controller.get_text_surface(f'$ {self.player.money:.2f}', colors.GREEN, self.font(25))
        txt_money_rect = txt_money.get_rect()
        txt_money_rect.left = p1_icon_rect.right + 15
        txt_money_rect.centery = txt_store_title_rect.centery
        self.money_rect = txt_money_rect
        
        
        #   --drawing--
        
        #panels
        self.image.blit(ammo_panel, ammo_panel_rect)
        self.image.blit(items_panel, items_panel_rect)
        self.image.blit(weapons_panel, weapons_panel_rect)
        
        #scroll bars
        self.ammo_h_scrollbar.draw(self.image, self.store_v_scrollbar.scroll_offset - self.panel_margin/2)
        self.items_h_scrollbar.draw(self.image, self.store_v_scrollbar.scroll_offset - self.panel_margin/2)
        self.weapons_h_scrollbar.draw(self.image, self.store_v_scrollbar.scroll_offset - self.panel_margin/2)
        self.store_v_scrollbar.draw(self.image, - self.panel_margin/2)
        
        #buttons
        for b in self.buttons:
            b.draw(self.image, -self.panel_margin/2)
            
        
        #store header
        pygame.draw.rect(self.image, colors.BLACK, ((0,0), (image_rect.width, txt_store_title_rect.height + 10)))
        self.image.blit(txt_store_title, txt_store_title_rect)
        
        self.image.blit(p1_icon, p1_icon_rect)
        self.image.blit(txt_money, txt_money_rect)
        self.buttons[0].draw(self.image, -self.panel_margin/2)

        #item description
        _description_rect = pygame.Rect((image_rect.width - _item_description_size.x,0), _item_description_size)
        if self.selected_card != None:
            #btn buy
            btn_buy = self.buttons[1]
            btn_buy.rect.bottomleft = _description_rect.bottomleft + self.panel_margin/2 + vec(10,-10)
            
            _divider_line_left = btn_buy.rect.right - self.panel_margin.x/2 + 10
                
            #icon
            icon = game_controller.scale_image(pygame.image.load(self.selected_card.icon_path), 4)
            icon_rect = icon.get_rect()
            icon_rect.centerx = _description_rect.left + btn_buy.rect.width/2 + 10
            icon_rect.bottom = _description_rect.bottom - btn_buy.rect.height - 20
            
            #card title
            txt_card_title = menu_controller.get_text_surface(self.selected_card.title, colors.WHITE, self.font(25))
            txt_card_title_rect = txt_card_title.get_rect()
            txt_card_title_rect.centerx = icon_rect.centerx
            txt_card_title_rect.bottom = icon_rect.top - 5
            
            #bullets
            bullet_text = ""
            p = self.player
            
            bullet_text = f'{p.backpack.get_ammo(p.current_weapon.bullet_type)}/{p.backpack.get_max_ammo(p.current_weapon.bullet_type)}'
            
            if len(bullet_text) > 0:
                txt_bullets = menu_controller.get_text_surface(bullet_text, colors.WHITE, self.font(20))
                txt_bullets_rect = txt_bullets.get_rect()
                icon_rect.left -= txt_bullets_rect.width/2 + 2.5
                txt_bullets_rect.centery = icon_rect.centery
                txt_bullets_rect.left = icon_rect.right + 5
                
                
                
            #drawing
            pygame.draw.rect(self.image, colors.BLACK, _description_rect)
            pygame.draw.rect(self.image, colors.LIGHT_GRAY, _description_rect, 2)
            self.buttons[1].draw(self.image, -self.panel_margin/2)
            self.image.blit(icon, icon_rect)
            if len(bullet_text) > 0:
                self.image.blit(txt_bullets, txt_bullets_rect)
            self.image.blit(txt_card_title, txt_card_title_rect)
            #divider line
            pygame.draw.line(self.image, colors.LIGHT_GRAY, (_divider_line_left, 10), (_divider_line_left, _description_rect.bottom - 10), 2)
            
            #description
            lines = [menu_controller.get_text_surface(line, colors.WHITE, self.font(18)) for line in self.selected_card.description.split("\n")]
            _line_space = 20
            _description_margin = vec(15,20)
            for i, line in enumerate(lines):
                line_rect = line.get_rect()
                line_rect.left = _divider_line_left + _description_margin.x
                line_rect.top = _description_rect.top + _description_margin.y +_line_space * i
                self.image.blit(line, line_rect)
            
        screen.blit(self.image, image_rect)
       
            
            
    def buy_ammo(self, ammo_type: enums.BulletType):
        item = self.selected_card
        b = self.player.backpack
        
        if not b.can_carry_ammo(item.count, self.player.current_weapon.bullet_type):
            return False
        
        b.set_ammo(b.get_ammo(ammo_type) + item.count, ammo_type)
        
        return True
                
            
    def process_purchase(self):
        item = self.selected_card
        bought = False
        
        if self.player.money < item.price:
            return
        
        if item.item_name.endswith("ammo"):
            bought = self.buy_ammo(item.bullet_type)
            
            
            
        if bought:
            self.player.money -= item.price
            
            menu_controller.popup(Popup(f"-${item.price}", vec(self.money_rect.topleft), **constants.POPUPS["damage"]))