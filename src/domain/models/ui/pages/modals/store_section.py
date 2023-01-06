import pygame
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller, resources
from domain.utils import colors, constants, enums
from domain.models.ui.button import Button
from domain.models.ui.popup_text import Popup
from domain.models.ui.scrollbar import ScrollBar
from domain.models.ui.store_item import StoreItem
from domain.models.ui.attribute_bars import AttributeBar
from domain.content.weapons.melee import Melee
from domain.content.weapons.semi_auto import SemiAuto
from domain.content.weapons.shotgun import Shotgun
from domain.content.weapons.full_auto import FullAuto
from domain.content.weapons.launcher import Launcher
from domain.content.weapons.sniper import Sniper
from domain.models.weapon import Weapon


class Store:
    def __init__(self, player: Player, panel_margin: vec, **kwargs):
        
        self.player = player
        self.panel_margin = panel_margin
        self.store_v_scrollbar: ScrollBar = None
        self.purchase_sound = pygame.mixer.Sound(f'{resources.SOUNDS_PATH}sound_effects\\ui\\purchase.mp3')
        self.purchase_sound.set_volume(0.3)
        
        
        self.ammo_h_scrollbar: ScrollBar = None
        self.items_h_scrollbar: ScrollBar = None
        self.weapons_h_scrollbar: ScrollBar = None
        self.image: pygame.Surface = None
        self.on_return = kwargs.pop("on_return", lambda: None)
        
        self.money_rect: pygame.Rect = None
        
        self.selected_card: StoreItem = None
        self.selected_weapon: Weapon = None
        self.card_size = vec(100,100)
        
        _cards_descriptions = {
            "pistol_ammo": "It's ammo, for a pistol.\nYou put it in a pistol and fire...\nWhat else shoud it be?",
            "shotgun_ammo": "Why shoot one bullet if you can\nshoot 12 at once?",
            "rifle_ammo": "Auto fire goes brrrrrrrrr",
            "sniper_ammo": "They won't know what hit'em!",
            "rocket_ammo": "Booooom!",
            
            "machete": "tags:melee, small-damage\nThe ultimate multi-purpose tool\nfor cutting brains and slicing\nthrough fresh zombies. It's also\ngreat for chopping up onions\nand tomatoes! Two tools in one!",
            "p_1911": "tags:Semi-auto, medium-damage\nIt's an old weapon, but it is\nreliable enough. Or is it?",
            "short_barrel": "tags:Pump-action, high-damage\nThis little shotgun packs a big\npunch! Don't let its compact size\nfool you, it may be small enough to\nfit in your pocket, but it can kill\nan elephant with a single shot!",
            "uzi": "tags:Auto-fire, small-damage\nUZI with caution!\nYou'll run out of bullets before\nyou can say OH CRAP.",
            "rpg": "tags:Area-damage, high-damage\nThis bad boy is guaranteed to blow\nthose brain-hungry back to the\ngrave! Send chunks of zombie\nflying in the air! But One wrong\nmove and you'll join 'em yourself!",
            
            "first_aid_kit": "tags:Restores your health partially.\nDon't let a little digital bloodshed\nslow you down. Heal it back up\nbefore it becomes a truly mess!",
            "medkit": "tags:Completely restores your health.\nIn a world of virtual zombies and\npixels, the medkit is your best\nfriend. Just a quick tap and you'll\nbe back to 100% health in no time!",
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
            StoreItem(f'{resources.IMAGES_PATH}ui\\pistol_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Pistol Ammo", item_name = "pistol_ammo", price = 20, count = 10, bullet_type = enums.BulletType.PISTOL, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\shotgun_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Shotgun Ammo", item_name = "shotgun_ammo", price = 30, count = 5, bullet_type = enums.BulletType.SHOTGUN, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\rifle_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rifle Ammo", item_name = "rifle_ammo", price = 45, count = 30, bullet_type = enums.BulletType.ASSAULT_RIFLE, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\sniper_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Sniper Ammo", item_name = "sniper_ammo", price = 40, count =5, bullet_type = enums.BulletType.SNIPER, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\rocket_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rocket Ammo", item_name = "rocket_ammo", price = 135, count =1, bullet_type = enums.BulletType.ROCKET, **cards_dict)
        ]
        
        self.items:list[StoreItem] = [
            StoreItem(f'{resources.IMAGES_PATH}items\\first_aid_kit.png', pygame.Rect((0,0), self.card_size), "First Aid Kit", item_name = "first_aid_kit", price = 75, count = 30, icon_scale = 0.9, store_icon_scale = 1.9, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}items\\medkit.png', pygame.Rect((0,0), self.card_size), "MedKit", item_name = "medkit", price = 230, count = 0,icon_scale = 1.2,store_icon_scale = 2, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True),
            StoreItem(f'{resources.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True)
        ]
        
        self.weapons:list[StoreItem] = [
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.MACHETE, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "Machete", item_name = "machete", price = 0, icon_scale = 0.2, store_icon_scale = 0.1, bullet_type = enums.BulletType.MELEE, weapon_type = enums.Weapons.MACHETE, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.P_1911, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "Colt 1911", item_name = "p_1911", price = 80, store_icon_scale = 2, bullet_type = enums.BulletType.PISTOL, weapon_type = enums.Weapons.P_1911, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.SHORT_BARREL, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "Short Barrel", item_name = "short_barrel", price = 500, icon_scale = 1.8, store_icon_scale = 0.3, bullet_type = enums.BulletType.SHOTGUN, weapon_type = enums.Weapons.SHORT_BARREL, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.UZI, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "UZI", item_name = "uzi", price = 750, icon_scale = 1.1, store_icon_scale = 2.3, bullet_type = enums.BulletType.PISTOL, weapon_type = enums.Weapons.UZI, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.RPG, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "RPG", item_name = "rpg", price = 1200, icon_scale = 2.2, store_icon_scale = 0.14, bullet_type = enums.BulletType.ROCKET, weapon_type = enums.Weapons.RPG, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True)
        ]
        
        self.cards_list = [*self.ammos, *self.items, *self.weapons]
        for c in self.cards_list:
            c.description = _cards_descriptions.pop(c.item_name, "")
            
        
        
        self.ammo_panel_buttons = [
                Button((0,0), f'{resources.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_forward(100)),
                Button((0,0), f'{resources.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.ammo_h_scrollbar.move_backward(100))
            ]
        
        self.items_panel_buttons = [
                Button((0,0), f'{resources.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_forward(100)),
                Button((0,0), f'{resources.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.items_h_scrollbar.move_backward(100))
            ]
        
        self.weapons_panel_buttons = [
                Button((0,0), f'{resources.IMAGES_PATH}ui\\left_arrow.png', scale = 1.7, on_click = lambda: self.weapons_h_scrollbar.move_forward(100)),
                Button((0,0), f'{resources.IMAGES_PATH}ui\\right_arrow.png', scale = 1.7, on_click = lambda: self.weapons_h_scrollbar.move_backward(100))
            ]
        
        self.buttons: list[Button] = [
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{resources.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = self.on_return),
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{resources.IMAGES_PATH}ui\\btn_small_green.png', text_font = resources.px_font(20), text_color = colors.BLACK, scale=1.4, visible = False, hover_scale=1, on_click = self.process_purchase)
            ]
        
        self.attributes_max = {
            "damage": 50,
            "firerate": 15,
            "reload_speed": 10,
            "range": 1000
        }
        
        self.buttons.extend([*self.ammo_panel_buttons, *self.items_panel_buttons, *self.weapons_panel_buttons])
    
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
            
            
        
            
        bck = self.player.backpack
        
        #if there is any item selected
        if self.selected_card != None:
            btn_buy = self.buttons[1]
            btn_text = ""
            _card_equiped = False
            #if the player has the item
            if self.selected_card.owned:
                #if the item is a weapon
                if self.selected_card.weapon_type != None:
                    weapon = bck.get_weapon(self.selected_card.weapon_type)
                    #if player really has this weapon
                    if weapon != None:
                        #if this weapon is the equiped primary or secondary
                        if bck.equipped_primary == self.selected_card.weapon_type or bck.equipped_secondary == self.selected_card.weapon_type:
                            btn_text = "Equiped"
                            _card_equiped = True
                        else: #otherwise it's just in the inventory
                            btn_text = "Equip " + ("Primary" if weapon.is_primary else "Secondary")
                else: #not a weapon
                    btn_text = "Purchased"

            else: #player doesn't have the item
                
                btn_text = f'Buy{" +" + str(self.selected_card.count) if self.selected_card.count > 0 else ""}'
                
            btn_buy.set_text(btn_text)
            #if the player can afford to buy the item
            _has_money = self.player.money >= self.selected_card.price
            
            #disables btn buy if already has the item and it's not equiped and it's not a healthkit with full health 
            btn_buy.enable((_has_money or self.selected_card.owned) and not _card_equiped and not (self.selected_card.item_name.endswith("kit") and self.player.health >= self.player.max_health))

        for card in self.cards_list:
            if card.weapon_type != None and bck.get_weapon(card.weapon_type) != None:
                card.owned = True
            card.update(self.panel_margin/2, self.player.money)
            
    def get_weapon_or_default(self, weapon_type: enums.Weapons):
        w = self.player.backpack.get_weapon(weapon_type)
        if w != None:
            return w
        
        match weapon_type:
            case enums.Weapons.MACHETE:
                return Melee(vec(0,0), load_content = False)
            
            case enums.Weapons.P_1911:
                return SemiAuto(vec(0,0), load_content = False)
                
            case enums.Weapons.SHORT_BARREL:
                return Shotgun(vec(0,0), load_content = False)
                
            case enums.Weapons.UZI:
                return FullAuto(vec(0,0), load_content = False)
            
            case enums.Weapons.RPG:
                return Launcher(vec(0,0), load_content = False)
            
            case enums.Weapons.SV98:
                return Sniper(vec(0,0), load_content = False)

            
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
        
        title = menu_controller.get_text_surface(title_text, colors.WHITE, resources.px_font(50))
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
        txt_store_title = menu_controller.get_text_surface("Store", colors.WHITE, resources.px_font(80))
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
            
            
        p1_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png'), 2.5, convert_type=enums.ConvertType.CONVERT_ALPHA)
        p1_icon_rect = p1_icon.get_rect()
        p1_icon_rect.left = txt_store_title_rect.right + 30
        p1_icon_rect.centery = txt_store_title_rect.centery

        txt_money = menu_controller.get_text_surface(f'$ {self.player.money:.2f}', colors.GREEN, resources.px_font(25))
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
            
            _v_divider_line_left = btn_buy.rect.right - self.panel_margin.x/2 + 10
                
            #card title
            txt_card_title = menu_controller.get_text_surface(self.selected_card.title, colors.WHITE, resources.px_font(25))
            txt_card_title_rect = txt_card_title.get_rect()
            txt_card_title_rect.centerx = _description_rect.left + btn_buy.rect.width/2 + 10
            txt_card_title_rect.top = _description_rect.top
            
            #icon
            icon = game_controller.scale_image(pygame.image.load(self.selected_card.icon_path), self.selected_card.store_icon_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
            icon_rect = icon.get_rect()
            icon_rect.centerx = txt_card_title_rect.centerx
            icon_rect.top = txt_card_title_rect.bottom + 10
            
            #bullets
            count_text = ""
            p = self.player
            
            if self.selected_card.bullet_type != None and self.selected_card.bullet_type != enums.BulletType.MELEE:
                count_text = f'{p.backpack.get_ammo(self.selected_card.bullet_type)}/{p.backpack.get_max_ammo(self.selected_card.bullet_type)}'
            if self.selected_card.item_name.endswith("kit"):
                count_text = f'{self.player.health}/{self.player.max_health}'
            
            if len(count_text) > 0:
                txt_bullets = menu_controller.get_text_surface(count_text, colors.WHITE, resources.px_font(20))
                txt_bullets_rect = txt_bullets.get_rect()
                icon_rect.left -= txt_bullets_rect.width/2 + 2.5
                txt_bullets_rect.centery = icon_rect.centery
                txt_bullets_rect.left = icon_rect.right + 5
                
            if self.selected_card.weapon_type != None:
                if self.selected_weapon == None or self.selected_weapon.weapon_type != self.selected_card.weapon_type:
                    self.selected_weapon = self.get_weapon_or_default(self.selected_card.weapon_type)
                
                weapon = self.selected_weapon
                
                #attribute bars
                _description_rect.height *= 1.8
                _bar_pos = vec(_description_rect.left + 10, _description_rect.top + _item_description_size.y + 10)
                _bars_margin = 10
                _bars_size = vec(_description_rect.width/1.65,15)
                
                _reload_speed = 0
                _damage = weapon.damage
                _range = 0
                match weapon.reload_type:
                    case enums.ReloadType.SINGLE_BULLET:
                        _reload_speed = 5000 / (weapon.reload_delay_ms * weapon.magazine_size)
                    case enums.ReloadType.NO_RELOAD:
                        _reload_speed = 0
                    case _:
                        _reload_speed = 5000 / weapon.reload_delay_ms
                
                match weapon.fire_mode:
                    case enums.FireMode.MELEE:
                        _range = 0
                    case _:
                        _range = (weapon.bullet_min_range + weapon.bullet_max_range)/2
                        
                if weapon.bullet_type == enums.BulletType.SHOTGUN and weapon.ballin_count != None:
                    _damage = weapon.damage * weapon.ballin_count
            
                _damage_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*0), _bars_size), max_value = self.attributes_max["damage"], value = _damage, **constants.ATTRIBUTE_BARS["weapon"])
                _firerate_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*1), _bars_size), max_value = self.attributes_max["firerate"], value = weapon.fire_rate, **constants.ATTRIBUTE_BARS["weapon"])
                _reload_speed_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*2), _bars_size), max_value = self.attributes_max["reload_speed"], value = _reload_speed, **constants.ATTRIBUTE_BARS["weapon"])
                _range_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*3), _bars_size), max_value = self.attributes_max["range"], value = _range, **constants.ATTRIBUTE_BARS["weapon"])

                #attribute labels
                _txt_damage = menu_controller.get_text_surface("Damage:", colors.WHITE, resources.px_font(25))
                _txt_damage_rect = _txt_damage.get_rect()
                _txt_damage_rect.centery = _damage_bar.rect.centery
                _txt_damage_rect.left = _bar_pos.x
                
                _txt_firerate = menu_controller.get_text_surface("Fire rate:", colors.WHITE, resources.px_font(25))
                _txt_firerate_rect = _txt_firerate.get_rect()
                _txt_firerate_rect.centery = _firerate_bar.rect.centery
                _txt_firerate_rect.left = _bar_pos.x
                
                _txt_reload_speed = menu_controller.get_text_surface("Reload speed:", colors.WHITE, resources.px_font(25))
                _txt_reload_speed_rect = _txt_reload_speed.get_rect()
                _txt_reload_speed_rect.centery = _reload_speed_bar.rect.centery
                _txt_reload_speed_rect.left = _bar_pos.x
                
                _txt_range = menu_controller.get_text_surface("Range:", colors.WHITE, resources.px_font(25))
                _txt_range_rect = _txt_range.get_rect()
                _txt_range_rect.centery = _range_bar.rect.centery
                _txt_range_rect.left = _bar_pos.x
                
                _max_txt_width = max([x.width for x in [_txt_damage_rect, _txt_firerate_rect, _txt_reload_speed_rect, _txt_range_rect]])
                _txt_left = _txt_damage_rect.left + _max_txt_width + _bars_margin
                _damage_bar.rect.left = _txt_left
                _firerate_bar.rect.left = _txt_left
                _reload_speed_bar.rect.left = _txt_left
                _range_bar.rect.left = _txt_left

            #drawing
            pygame.draw.rect(self.image, colors.BLACK, _description_rect)
            pygame.draw.rect(self.image, colors.LIGHT_GRAY, _description_rect, 2)
            self.buttons[1].draw(self.image, -self.panel_margin/2)
            self.image.blit(icon, icon_rect)
            if len(count_text) > 0:
                self.image.blit(txt_bullets, txt_bullets_rect)
            self.image.blit(txt_card_title, txt_card_title_rect)
            if self.selected_card.weapon_type != None:
                _damage_bar.draw(self.image, vec(0,0))
                self.image.blit(_txt_damage, _txt_damage_rect)
                
                _firerate_bar.draw(self.image, vec(0,0))
                self.image.blit(_txt_firerate, _txt_firerate_rect)

                _reload_speed_bar.draw(self.image, vec(0,0))
                self.image.blit(_txt_reload_speed, _txt_reload_speed_rect)
                
                _range_bar.draw(self.image, vec(0,0))
                self.image.blit(_txt_range, _txt_range_rect)
                
            #vertical divider line
            pygame.draw.line(self.image, colors.LIGHT_GRAY, (_v_divider_line_left, 10), (_v_divider_line_left, _description_rect.top + _item_description_size.y - 10), 2)
            #horizontal divider line
            pygame.draw.line(self.image, colors.LIGHT_GRAY, (_description_rect.left, _description_rect.top + _item_description_size.y), (_description_rect.right, _item_description_size.y), 2)
            
            #description
            lines = [menu_controller.get_text_surface(line.replace("tags:",""), colors.YELLOW if line.startswith("tags:") else colors.WHITE, resources.px_font(18)) for line in self.selected_card.description.split("\n")]
            _line_space = 20
            _description_margin = vec(10,20)
            for i, line in enumerate(lines):
                line_rect = line.get_rect()
                line_rect.left = _v_divider_line_left + _description_margin.x
                line_rect.top = _description_rect.top + _description_margin.y +_line_space * i
                self.image.blit(line, line_rect)
            
        screen.blit(self.image, image_rect)
       
            
    def buy_weapon(self, weapon_type: enums.Weapons):
        return self.player.add_weapon(weapon_type)
            
    def buy_ammo(self, ammo_type: enums.BulletType):
        item = self.selected_card
        b = self.player.backpack
        
        if not b.can_carry_ammo(item.count, ammo_type):
            return False
        
        b.set_ammo(b.get_ammo(ammo_type) + item.count, ammo_type)
        
        return True
                
            
    def process_purchase(self):
        item = self.selected_card
        bought = False
        
        if self.player.money < item.price and not item.owned:
            return
        
        if item.item_name.endswith("ammo"):
            bought = self.buy_ammo(item.bullet_type)
        
        if item.weapon_type != None:
            if item.owned:
                w = self.player.backpack.equip_weapon(item.weapon_type)
                self.player.current_weapon = w
            else:
                bought = self.buy_weapon(item.weapon_type)
                
        if item.item_name.endswith("kit"):
            self.player.get_health(item.count if item.count > 0 else 9999)
            bought = True
            
            
            
        if bought:
            self.player.money -= item.price
            self.purchase_sound.play()
            
            menu_controller.popup(Popup(f"-${item.price}", vec(self.money_rect.topleft), **constants.POPUPS["damage"]))