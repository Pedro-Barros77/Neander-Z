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
from domain.models.weapon import Weapon


class Inventory:
    def __init__(self, player: Player, panel_margin: vec, **kwargs):
        
        self.player = player
        self.panel_margin = panel_margin
        self.store_v_scrollbar: ScrollBar = None
        self.sell_sound = pygame.mixer.Sound(f'{resources.SOUNDS_PATH}sound_effects\\ui\\purchase.mp3')
        self.sell_sound.set_volume(0.3)
        
        
        self.image: pygame.Surface = None
        self.on_return = kwargs.pop("on_return", lambda: None)
        
        self.selected_card: StoreItem = None
        self.card_size = vec(100,100)
        
        def _select_card(card: StoreItem):
            card.default_on_click()
            self.selected_card = card
        
        def _unselect_card(card: StoreItem):
            btns_hovered = [b for b in self.buttons if b.hovered]
            scroll_bars_held = [s for s in [self.store_v_scrollbar] if s.holding_bar]
            
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
            StoreItem(f'{resources.IMAGES_PATH}ui\\rocket_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rocket Ammo", item_name = "rocket_ammo", price = 80, count =1, bullet_type = enums.BulletType.ROCKET, **cards_dict)
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
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.UZI, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "UZI", item_name = "uzi", price = 650, icon_scale = 1.1, store_icon_scale = 2.3, bullet_type = enums.BulletType.PISTOL, weapon_type = enums.Weapons.UZI, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.P_93r, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "Beretta 93R", item_name = "93r", price = 730, icon_scale = 1.1, store_icon_scale = 1.5, bullet_type = enums.BulletType.PISTOL, weapon_type = enums.Weapons.P_93r, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.M16, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "M16", item_name = "m16", price = 800, icon_scale = 2, store_icon_scale = 1.7, bullet_type = enums.BulletType.ASSAULT_RIFLE, weapon_type = enums.Weapons.M16, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.SV98, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "SV98", item_name = "sv98", price = 900, icon_scale = 2.3, store_icon_scale = 1.1, bullet_type = enums.BulletType.SNIPER, weapon_type = enums.Weapons.SV98, **cards_dict),
            StoreItem(f'{resources.get_weapon_path(enums.Weapons.RPG, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), "RPG", item_name = "rpg", price = 1200, icon_scale = 2.2, store_icon_scale = 0.14, bullet_type = enums.BulletType.ROCKET, weapon_type = enums.Weapons.RPG, **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\lock.png', pygame.Rect((0,0), self.card_size), "Locked", locked = True)
        ]
        
        self.cards_list = [*self.ammos, *self.items, *self.weapons]
        
        
        self.buttons: list[Button] = [
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{resources.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = self.on_return),
            ]
        
        self.attributes_max = kwargs.pop("attributes_max",{
            "damage": 50,
            "firerate": 15,
            "reload_speed": 10,
            "range": 1000
        })
        
    def update(self, **kwargs):
        events = kwargs.pop("events", [])
        
        for e in events:
            if self.store_v_scrollbar != None:
                self.store_v_scrollbar.event_handler(e)
                self.store_v_scrollbar.update()
                
        for b in self.buttons:
            b.update()
            
        bck = self.player.backpack
        
        for card in self.cards_list:
            card.update(self.panel_margin/2, self.player.money)
            
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        if self.image == None:
            self.image = pygame.Surface(screen_rect.size - self.panel_margin, pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        image_rect = self.image.get_rect()
        image_rect.topleft = self.panel_margin/2
        
        #title
        txt_inv_title = menu_controller.get_text_surface("Inventory", colors.WHITE, resources.px_font(80))
        txt_store_title_rect = txt_inv_title.get_rect()
        txt_store_title_rect.topleft = vec(self.buttons[0].rect.right, 10)

        if self.store_v_scrollbar == None:
            self.store_v_scrollbar = ScrollBar(enums.Orientation.VERTICAL, vec(1,(screen_rect.height-self.panel_margin.y) *2), pygame.Rect((screen_rect.width - self.panel_margin.x, self.panel_margin.y + txt_store_title_rect.height), (20,screen_rect.height - self.panel_margin.y*2 - txt_store_title_rect.height)), use_arrows = False)
            
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
        
        #scroll bars
        self.store_v_scrollbar.draw(self.image, - self.panel_margin/2)
        
        #buttons
        for b in self.buttons:
            b.draw(self.image, -self.panel_margin/2)
        
        #inventory header
        pygame.draw.rect(self.image, colors.BLACK, ((0,0), (image_rect.width, txt_store_title_rect.height + 10)))
        self.image.blit(txt_inv_title, txt_store_title_rect)
        
        self.image.blit(p1_icon, p1_icon_rect)
        self.image.blit(txt_money, txt_money_rect)
        self.buttons[0].draw(self.image, -self.panel_margin/2)

        screen.blit(self.image, image_rect)