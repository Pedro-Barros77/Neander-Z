import pygame, datetime
from pygame.math import Vector2 as vec

from domain.models.player import Player
from domain.services import menu_controller, game_controller, resources
from domain.utils import colors, constants, enums, math_utillity as math
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
        self.inv_v_scrollbar: ScrollBar = None
        self.purchase_sound = pygame.mixer.Sound(f'{resources.SOUNDS_PATH}sound_effects\\ui\\purchase.mp3')
        self.purchase_sound.set_volume(0.3)
        
        
        self.image: pygame.Surface = None
        self.on_return = kwargs.pop("on_return", lambda: None)
        self.start_time = datetime.datetime.now()
        
        self.selected_card: StoreItem = None
        self.selected_weapon: Weapon = None
        self.card_size = vec(100,100)
        
        self.weapons: list[StoreItem] = []
        self.items:list[StoreItem] = []
        self.cards_list = []
        self.buttons: list[Button] = []
        
        self.weapon_attributes_max = kwargs.pop("weapon_attributes_max",{
            "damage": 50,
            "firerate": 15,
            "reload_speed": 10,#5000
            "range": 1000,
            "concentration": 12,#90
            "magazine_size": 50,
            "stamina": 6 #6
        })
        
        self.player_attributes_max = kwargs.pop("player_attributes_max",{
            "max_health": 360,
            "movement_speed": 0.7,
            "sprint_speed": 1.3,
            "jump_force": 11,
            "max_stamina": 1500,
            "stamina_regen_rate": 9,
            "stamina_regen_haste": 18,#5000
            "jump_stamina_skill": 50,#100
            "sprint_stamina_skill": 60,#100
            "attack_stamina_skill": 100 #10
        })
        
        #weapons
        self.damage_bar = None
        self.firerate_bar = None
        self.reload_bar = None
        self.range_bar = None
        self.magazine_bar = None
        self.concentration_bar = None
        self.stamina_bar = None
        
        #player
        self.max_health_bar = None
        self.movement_speed_bar = None
        self.sprint_speed_bar = None
        self.jump_force_bar = None
        
        self.max_stamina_bar = None
        self.stamina_regen_rate_bar = None
        self.stamina_regen_haste_bar = None
        self.jump_stamina_skill_bar = None
        self.sprint_stamina_skill_bar = None
        self.attack_stamina_skill_bar = None
        
        self.load_inventory()
        
        self.ammos:list[StoreItem] = [
            # StoreItem(f'{resources.IMAGES_PATH}ui\\pistol_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Pistol Ammo", item_name = "pistol_ammo", price = 20, count = 10, bullet_type = enums.BulletType.PISTOL, **cards_dict),
            # StoreItem(f'{resources.IMAGES_PATH}ui\\shotgun_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Shotgun Ammo", item_name = "shotgun_ammo", price = 30, count = 5, bullet_type = enums.BulletType.SHOTGUN, **cards_dict),
            # StoreItem(f'{resources.IMAGES_PATH}ui\\rifle_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rifle Ammo", item_name = "rifle_ammo", price = 45, count = 30, bullet_type = enums.BulletType.ASSAULT_RIFLE, **cards_dict),
            # StoreItem(f'{resources.IMAGES_PATH}ui\\sniper_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Sniper Ammo", item_name = "sniper_ammo", price = 40, count =5, bullet_type = enums.BulletType.SNIPER, **cards_dict),
            # StoreItem(f'{resources.IMAGES_PATH}ui\\rocket_ammo_icon.png', pygame.Rect((0,0), self.card_size), "Rocket Ammo", item_name = "rocket_ammo", price = 80, count =1, bullet_type = enums.BulletType.ROCKET, **cards_dict)
        ]
        
        
        self.pistol_ammo_icon = None
        self.shotgun_ammo_icon = None
        self.rifle_ammo_icon = None
        self.sniper_ammo_icon = None
        self.rocket_ammo_icon = None
        
            
    def load_inventory(self):
        self.weapons.clear()
        self.items.clear()
        self.cards_list.clear()
        self.buttons.clear()
        
        #region cards callbacks
        def _select_card(card: StoreItem):
            card.default_on_click()
            self.selected_card = card
        
        def _unselect_card(card: StoreItem):
            btns_hovered = [b for b in self.buttons if b.hovered and "equip" not in b.name]
            scroll_bars_held = [s for s in [self.inv_v_scrollbar] if s.holding_bar]
            
            if len(btns_hovered) > 0 or len(scroll_bars_held) > 0:
                return
            
            for b in self.buttons:
                if b.name.startswith("btn_upgrade"):
                    b.visible = False
            
            card.default_on_blur()
            if self.selected_card != None and self.selected_card.item_name == card.item_name:
                self.selected_card = None 
        #endregion
        
        cards_dict = {
            "on_click": _select_card,
            "on_blur": _unselect_card,
            "owned": True
        }  
         
        #Weapons
        for w in [*self.player.backpack.primary_weapons, *self.player.backpack.secondary_weapons]:
            self.weapons.append(
                StoreItem(f'{resources.get_weapon_path(w.weapon_type, enums.AnimActions.ICON)}', pygame.Rect((0,0), self.card_size), w.display_name, item_name = str(w.weapon_type.value), price = 0, icon_scale = w.store_scale, bullet_type = w.bullet_type, weapon_type = w.weapon_type, **cards_dict)
            )
            
        self.items.extend([
            StoreItem(f'{resources.IMAGES_PATH}items\\backpack.png', pygame.Rect((0,0), self.card_size), "Backpack", item_name = "backpack", price = 0, count = 0, icon_scale = 1, store_icon_scale = 1, price_text=" ", **cards_dict),
            StoreItem(f'{resources.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png', pygame.Rect((0,0), self.card_size), "Player", item_name = "player", price = 0, count = 0, icon_scale = 1, store_icon_scale = 1, price_text=" ", **cards_dict),
        ])
            
        #Cards
        self.cards_list = [*self.weapons, *self.items]#*self.ammos,
        
        #Buttons
        self.buttons = [
                Button(vec(self.panel_margin.x, self.panel_margin.y), f'{resources.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = self.on_return),
                Button(vec(0,0), f'{resources.IMAGES_PATH}ui\\btn_small_green.png', text="", text_color = colors.BLACK, text_font = resources.px_font(25), scale = 2, name="sell_weapon", on_click = lambda: self.sell_weapon(self.selected_card.weapon_type)),
                Button(vec(0,0), f'{resources.IMAGES_PATH}ui\\swap.png', scale = 1, name="swap_slots", on_click = self.swap_weapon_slots),
                Button(vec(0,0), f'{resources.IMAGES_PATH}ui\\btn_small_green.png', text="Upgrade for $0.00", text_color = colors.BLACK, text_font = resources.px_font(23), scale = 2, name="upgrade_backpack", on_click = self.upgrade_backpack),
            ]
        
        weapons_btn_dict = {
            "scale": 1.6,
            "text_color": colors.BLACK,
            "text_font": resources.px_font(20)
        }
        
        #Weapons buttons
        self.buttons.extend(
            [
                *[Button(vec(0,0), f'{resources.IMAGES_PATH}ui\\btn_small_green.png', on_click = lambda w_type = w.weapon_type: self.equip_weapon(w_type, True), name = f'equip-primary_{w.weapon_type.value}', **weapons_btn_dict) for w in self.weapons],
                *[Button(vec(0,0), f'{resources.IMAGES_PATH}ui\\btn_small_green.png', on_click = lambda w_type = w.weapon_type: self.equip_weapon(w_type), name = f'equip-secondary_{w.weapon_type.value}', **weapons_btn_dict) for w in self.weapons],
            ]
        )
        
        #Upgrades buttons
        for att in self.weapon_attributes_max.keys():
            self.buttons.append(
                Button((0,0), f'{resources.IMAGES_PATH}ui\\plus.png', on_click = lambda: print("click"), text_font = resources.px_font(20),name = f'btn_upgrade_weapon_{att}', text_color = colors.BLACK, scale = 0.5, visible = False)
            )
        for att in self.player_attributes_max.keys():
            self.buttons.append(
                Button((0,0), f'{resources.IMAGES_PATH}ui\\plus.png', on_click = lambda: print("click"), text_font = resources.px_font(20),name = f'btn_upgrade_player_{att}', text_color = colors.BLACK, scale = 0.5, visible = False)
            )
        
    def update(self, **kwargs):
        events = kwargs.pop("events", [])
        
        for e in events:
            if self.inv_v_scrollbar != None:
                self.inv_v_scrollbar.event_handler(e)
                self.inv_v_scrollbar.update()
                
        if self.selected_card != None:
            self.buttons[1].visible = True
            if self.selected_card.item_name == "backpack":
                self.buttons[3].visible = True
            else:
                self.buttons[3].visible = False
        else:
            self.buttons[1].visible = False
            self.buttons[3].visible = False
                
        for b in self.buttons:
            b.update()
            
        bkp = self.player.backpack
        
        btn_upgrade_backpack = self.buttons[3]
        _has_bkp_upgrade = bkp.upgrade_step < len(constants.ITEMS_UPGRADES["backpack"])
        if _has_bkp_upgrade:
            btn_upgrade_backpack.set_text(f'Upgrade for ${constants.ITEMS_UPGRADES["backpack"][bkp.upgrade_step]["price"]:.2f}')
        if not _has_bkp_upgrade or (self.player.money < constants.ITEMS_UPGRADES["backpack"][bkp.upgrade_step]["price"] and btn_upgrade_backpack.enabled):
            btn_upgrade_backpack.set_image(f'{resources.IMAGES_PATH}ui\\btn_small.png')
            btn_upgrade_backpack.hovered = False
            if not _has_bkp_upgrade:
                btn_upgrade_backpack.set_text("MAX")
            btn_upgrade_backpack.default_on_hover(btn_upgrade_backpack)
            btn_upgrade_backpack.enable(False)
        elif not btn_upgrade_backpack.enabled and self.player.money >= constants.ITEMS_UPGRADES["backpack"][bkp.upgrade_step]["price"] and _has_bkp_upgrade:
            btn_upgrade_backpack.set_image(f'{resources.IMAGES_PATH}ui\\btn_small_green.png')
            btn_upgrade_backpack.default_on_hover(btn_upgrade_backpack)
            btn_upgrade_backpack.enable(True)

        for card in self.cards_list:
            #if the item is a weapon
            if card.weapon_type != None:
                btn_equip_prim = [b for b in self.buttons if b.name == f"equip-primary_{card.weapon_type.value}"][0]
                btn_equip_sec = [b for b in self.buttons if b.name == f"equip-secondary_{card.weapon_type.value}"][0]
                
                _btn_margin = vec(15, 5)
                btn_equip_prim.rect.bottomleft = card.rect.bottomright + vec(_btn_margin.x,0) + self.panel_margin/2
                btn_equip_sec.rect.bottomleft = card.rect.bottomright + vec(_btn_margin.x,-btn_equip_prim.rect.height -_btn_margin.y) + self.panel_margin/2
                
                weapon = bkp.get_weapon(card.weapon_type)
                
                #if this weapon is the equiped primary or secondary
                if bkp.equipped_primary == card.weapon_type or bkp.equipped_secondary == card.weapon_type:
                    if btn_equip_prim.text != "Unequip":
                        btn_equip_prim.set_image(f'{resources.IMAGES_PATH}ui\\btn_small.png')
                        btn_equip_prim.text_surface = btn_equip_prim.start_text
                        btn_equip_prim.set_text("Unequip")
                    btn_equip_sec.visible = False
                    if bkp.equipped_primary == card.weapon_type:
                        card.price_text = "Primary"
                    else: 
                        card.price_text = "Secondary"
                else: #otherwise it's just in the inventory
                    card.price_text = " "
                    if btn_equip_prim.text == "Unequip":
                        btn_equip_prim.set_image(f'{resources.IMAGES_PATH}ui\\btn_small_green.png')
                        btn_equip_prim.text_surface = btn_equip_prim.start_text
                    
                    if weapon.is_primary:
                        btn_equip_prim.set_text("Equip primary")
                        btn_equip_sec.visible = False
                    else:
                        btn_equip_prim.set_text("Equip as primary")
                        btn_equip_sec.set_text("Equip as secondary")
                        btn_equip_sec.visible = True
            
            card.update(self.panel_margin/2, self.player.money)

            
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        if self.image == None:
            self.image = pygame.Surface(screen_rect.size - self.panel_margin, pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        image_rect = self.image.get_rect()
        image_rect.topleft = self.panel_margin/2
        
        bkp = self.player.backpack
        
        #title
        txt_inv_title = menu_controller.get_text_surface("Inventory", colors.WHITE, resources.px_font(80))
        txt_store_title_rect = txt_inv_title.get_rect()
        txt_store_title_rect.topleft = vec(self.buttons[0].rect.right, 10)
        
        header_rect = pygame.Rect((0,0), (image_rect.width, txt_store_title_rect.height + 10))
        
        p1_icon = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}ui\\characters\\{self.player.character.value}\\head_icon.png'), 2.5, convert_type=enums.ConvertType.CONVERT_ALPHA)
        p1_icon_rect = p1_icon.get_rect()
        p1_icon_rect.left = txt_store_title_rect.right + 30
        p1_icon_rect.centery = txt_store_title_rect.centery

        txt_money = menu_controller.get_text_surface(f'$ {self.player.money:.2f}', colors.GREEN, resources.px_font(25))
        txt_money_rect = txt_money.get_rect()
        txt_money_rect.left = p1_icon_rect.right + 15
        txt_money_rect.centery = txt_store_title_rect.centery
        self.money_rect = txt_money_rect
        
        txt_primary = menu_controller.get_text_surface('1:', colors.WHITE, resources.px_font(30))
        txt_primary_rect = txt_primary.get_rect()
        txt_primary_rect.left = txt_money_rect.right + 20
        txt_primary_rect.centery = txt_store_title_rect.centery
        
        _slot_size = header_rect.height * 0.7
        primary_slot_rect = pygame.Rect((txt_primary_rect.left + 20, 0), (_slot_size, _slot_size))
        primary_slot_rect.centery = txt_store_title_rect.centery
        
        primary_icon, primary_icon_rect = None, None
        if bkp.equipped_primary != None:
            primary_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_primary, enums.AnimActions.ICON))
            _max_dim = max(primary_icon.get_width(), primary_icon.get_height())
            _percentage = ((primary_slot_rect.width * 100 / _max_dim)/100) * 1.1
            primary_icon = game_controller.scale_image(primary_icon, _percentage, enums.ConvertType.CONVERT_ALPHA)
            primary_icon_rect = primary_icon.get_rect()
            primary_icon_rect.center = primary_slot_rect.center
        
        btn_swap = self.buttons[2]
        if btn_swap.rect.topleft == (0,0):
            btn_swap.rect.centery = txt_store_title_rect.centery + self.panel_margin.y/2
            btn_swap.rect.left = primary_slot_rect.right + self.panel_margin.x/2 + 20
            btn_swap.set_pos(vec(btn_swap.rect.topleft))
        
        txt_secondary = menu_controller.get_text_surface('2:', colors.WHITE, resources.px_font(30))
        txt_secondary_rect = txt_secondary.get_rect()
        txt_secondary_rect.left = btn_swap.rect.right - self.panel_margin.x/2 + 20
        txt_secondary_rect.centery = txt_store_title_rect.centery
        
        secondary_slot_rect = pygame.Rect((txt_secondary_rect.left + 20, 0), (_slot_size, _slot_size))
        secondary_slot_rect.centery = txt_store_title_rect.centery
        
        secondary_icon, secondary_icon_rect = None, None
        if bkp.equipped_secondary != None:
            secondary_icon = pygame.image.load(resources.get_weapon_path(bkp.equipped_secondary, enums.AnimActions.ICON))
            _max_dim = max(secondary_icon.get_width(), secondary_icon.get_height())
            _percentage = ((secondary_slot_rect.width * 100 / _max_dim)/100) * 1.1
            secondary_icon = game_controller.scale_image(secondary_icon, _percentage, enums.ConvertType.CONVERT_ALPHA)
            secondary_icon_rect = secondary_icon.get_rect()
            secondary_icon_rect.center = secondary_slot_rect.center
        
        
        pnl_right = pygame.Surface((image_rect.width*0.62, image_rect.height - header_rect.height), pygame.SRCALPHA)
        pnl_right_rect = pygame.Rect((0,0), pnl_right.get_size())
        pnl_right_rect.topright = (image_rect.width,header_rect.height)

        if self.inv_v_scrollbar == None:
            self.inv_v_scrollbar = ScrollBar(enums.Orientation.VERTICAL, vec(1,(screen_rect.height-self.panel_margin.y) *2), pygame.Rect((pnl_right_rect.left + self.panel_margin.x/2 - 20, txt_store_title_rect.height + self.panel_margin.y/1.3), (20, image_rect.height - txt_store_title_rect.height - self.panel_margin.y/2)), use_arrows = False)
        
        #   --drawing--
        
        
        #right panel
        pnl_right.fill(colors.BLACK)
        pygame.draw.rect(pnl_right, colors.LIGHT_GRAY, ((0,0), pnl_right_rect.size), 1)
        
        #items
        _items_margin = vec(15, 50)
        for i, item in enumerate(self.cards_list):
            item.set_pos(vec(_items_margin.x, header_rect.height + _items_margin.y + (i * (_items_margin.y + self.card_size.y))) + self.inv_v_scrollbar.scroll_offset)
            item.draw(self.image, vec(0,0))
        
        #weapons buttons
        for b in [b for b in self.buttons if b.name.startswith("equip")]:
            b.draw(self.image, - self.panel_margin/2)
        
        #inventory header
        pygame.draw.rect(self.image, colors.BLACK, header_rect)
        self.image.blit(txt_inv_title, txt_store_title_rect)
        
        self.image.blit(p1_icon, p1_icon_rect)
        self.image.blit(txt_money, txt_money_rect)
        
        #primary slot
        self.image.blit(txt_primary, txt_primary_rect)
        pygame.draw.rect(self.image, colors.set_alpha(colors.WHITE, 100), primary_slot_rect, border_radius= 15)
        pygame.draw.rect(self.image, colors.LIGHT_PASTEL_BLUE, primary_slot_rect, 2, 15)
        if primary_icon != None:
            self.image.blit(primary_icon, primary_icon_rect)
            
        self.buttons[2].draw(self.image, -self.panel_margin/2)
        
        #secondary slot
        self.image.blit(txt_secondary, txt_secondary_rect)
        pygame.draw.rect(self.image, colors.set_alpha(colors.WHITE, 100), secondary_slot_rect, border_radius= 15)
        pygame.draw.rect(self.image, colors.LIGHT_PASTEL_BLUE, secondary_slot_rect, 2, 15)
        if secondary_icon != None:
            self.image.blit(secondary_icon, secondary_icon_rect)
            
        # self.buttons[0].draw(self.image, -self.panel_margin/2)
        _weapon_upgrade_btns = [b for b in self.buttons if b.name.startswith("btn_upgrade_weapon")]
        _player_upgrade_btns = [b for b in self.buttons if b.name.startswith("btn_upgrade_player")]
        if self.selected_card != None:
            if self.selected_card.weapon_type != None:
                if self.selected_weapon == None or self.selected_weapon.weapon_type != self.selected_card.weapon_type:
                    self.selected_weapon = self.get_weapon_or_default(self.selected_card.weapon_type)
                weapon = self.selected_weapon
                
                _txt_weapon_title = menu_controller.get_text_surface(weapon.display_name, colors.WHITE, resources.px_font(40))
                _txt_weapon_title_rect = _txt_weapon_title.get_rect()
                _txt_weapon_title_rect.top = 5
                _txt_weapon_title_rect.centerx = pnl_right_rect.width/2
                
                _bar_pos = vec(10, _txt_weapon_title_rect.bottom + 10)
                _bars_margin = 10
                _bars_size = vec(pnl_right_rect.width/2,15)
                
                _reload_speed = 0
                _concentration = 0
                _stamina_skill = 0
                _damage = weapon.damage
                _range = (weapon.bullet_min_range + weapon.bullet_max_range)/2
                _firerate = weapon.fire_rate
                _magazine_size = weapon.magazine_size
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
                        _stamina_skill = 6 / weapon.stamina_use
                    case enums.FireMode.BURST:
                        _firerate = (weapon.burst_fire_rate + weapon.fire_rate) / 2
                    case _:
                        pass
                                            
                if weapon.bullet_type == enums.BulletType.SHOTGUN and weapon.ballin_count != None:
                    _damage = weapon.damage * weapon.ballin_count
                    _concentration = 90 / weapon.dispersion
            
                #region Weapon bars
                if self.damage_bar == None:
                    self.damage_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*0), _bars_size), max_value = self.weapon_attributes_max["damage"], value = _damage, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.damage_bar.value = _damage
                    
                if self.firerate_bar == None:
                    self.firerate_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*1), _bars_size), max_value = self.weapon_attributes_max["firerate"], value = _firerate, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.firerate_bar.value = _firerate
                    
                if self.reload_bar == None:
                    self.reload_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*2), _bars_size), max_value = self.weapon_attributes_max["reload_speed"], value = _reload_speed, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.reload_bar.value = _reload_speed
                    
                if self.range_bar == None:
                    self.range_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*3), _bars_size), max_value = self.weapon_attributes_max["range"], value = _range, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.range_bar.value = _range
                    
                if self.magazine_bar == None:
                    self.magazine_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*4), _bars_size), max_value = self.weapon_attributes_max["magazine_size"], value = _magazine_size, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.magazine_bar.value = _magazine_size
                    
                if self.concentration_bar == None:
                    self.concentration_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*5), _bars_size), max_value = self.weapon_attributes_max["concentration"], value = _concentration, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.concentration_bar.value = _concentration

                if self.stamina_bar == None:
                    self.stamina_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*6), _bars_size), max_value = self.weapon_attributes_max["stamina"], value = _stamina_skill, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.stamina_bar.value = _stamina_skill
            #endregion
                
                #region Weapon attribute labels
                _txt_damage = menu_controller.get_text_surface("Damage:", colors.WHITE, resources.px_font(25))
                _txt_damage_rect = _txt_damage.get_rect()
                _txt_damage_rect.centery = self.damage_bar.rect.centery
                _txt_damage_rect.left = _bar_pos.x
                
                _txt_firerate = menu_controller.get_text_surface("Fire rate:", colors.WHITE if self.firerate_bar.value > 0 else colors.DARK_GRAY, resources.px_font(25))
                _txt_firerate_rect = _txt_firerate.get_rect()
                _txt_firerate_rect.centery = self.firerate_bar.rect.centery
                _txt_firerate_rect.left = _bar_pos.x
                
                _txt_reload_speed = menu_controller.get_text_surface("Reload speed:", colors.WHITE if self.reload_bar.value > 0 else colors.DARK_GRAY, resources.px_font(25))
                _txt_reload_speed_rect = _txt_reload_speed.get_rect()
                _txt_reload_speed_rect.centery = self.reload_bar.rect.centery
                _txt_reload_speed_rect.left = _bar_pos.x
                
                _txt_range = menu_controller.get_text_surface("Range:", colors.WHITE if self.range_bar.value > 0 else colors.DARK_GRAY, resources.px_font(25))
                _txt_range_rect = _txt_range.get_rect()
                _txt_range_rect.centery = self.range_bar.rect.centery
                _txt_range_rect.left = _bar_pos.x
                
                _txt_magazine = menu_controller.get_text_surface("Magazine size:", colors.WHITE if self.magazine_bar.value > 1 else colors.DARK_GRAY, resources.px_font(25))
                _txt_magazine_rect = _txt_magazine.get_rect()
                _txt_magazine_rect.centery = self.magazine_bar.rect.centery
                _txt_magazine_rect.left = _bar_pos.x
                
                _txt_concentration = menu_controller.get_text_surface("Concentration:", colors.WHITE if self.concentration_bar.value > 0 else colors.DARK_GRAY, resources.px_font(25))
                _txt_concentration_rect = _txt_concentration.get_rect()
                _txt_concentration_rect.centery = self.concentration_bar.rect.centery
                _txt_concentration_rect.left = _bar_pos.x

                _txt_stamina = menu_controller.get_text_surface("Stamina skill:", colors.WHITE if self.stamina_bar.value > 0 else colors.DARK_GRAY, resources.px_font(25))
                _txt_stamina_rect = _txt_stamina.get_rect()
                _txt_stamina_rect.centery = self.stamina_bar.rect.centery
                _txt_stamina_rect.left = _bar_pos.x
                
                _max_txt_width = max([x.width for x in [_txt_damage_rect, _txt_firerate_rect, _txt_reload_speed_rect, _txt_range_rect, _txt_magazine_rect, _txt_concentration_rect, _txt_stamina_rect]])
                _txt_left = _txt_damage_rect.left + _max_txt_width + _bars_margin/2
                self.damage_bar.rect.left = _txt_left
                self.firerate_bar.rect.left = _txt_left
                self.reload_bar.rect.left = _txt_left
                self.range_bar.rect.left = _txt_left
                self.magazine_bar.rect.left = _txt_left
                self.concentration_bar.rect.left = _txt_left
                self.stamina_bar.rect.left = _txt_left
                
                _attribute_bars = {
                    "damage": self.damage_bar,
                    "firerate": self.firerate_bar,
                    "reload_speed": self.reload_bar,
                    "range": self.range_bar,
                    "magazine_size": self.magazine_bar,
                    "concentration": self.concentration_bar,
                    "stamina": self.stamina_bar
                }
                
                for b in _attribute_bars.values():
                    if b.value == 0:
                        b.bar_border_color = colors.DARK_GRAY
                    else:
                        b.bar_border_color = b.start_bar_border_color
                
                _weapon_upgrades = constants.get_weapon_upgrade(self.selected_card.weapon_type)
                if _weapon_upgrades != None:
                    _unused_btns = [b for b in _weapon_upgrade_btns if b.name not in _weapon_upgrades.keys()]
                    for b in _unused_btns:
                        b.visible = False
                    
                    for key, value in _weapon_upgrades.items():
                        _btn_upgrade = [b for b in _weapon_upgrade_btns if key in b.name]
                        _bar = _attribute_bars[key]
                        if len(_btn_upgrade) <= 0 or _bar == None:
                            continue
                        _btn_upgrade = _btn_upgrade[0]
                        _btn_upgrade.rect.left = _bar.rect.right + self.panel_margin.x/2 + pnl_right_rect.left
                        _btn_upgrade.rect.centery = _bar.rect.centery + self.panel_margin.y/2 + pnl_right_rect.top
                        _btn_upgrade.visible = True
                        _btn_upgrade.on_click = lambda attr_name = key: self.buy_weapon_upgrade(self.selected_card.weapon_type, attr_name)
                        _upgrade_map_index = math.clamp(weapon.upgrades_map[key], 0, len(value)) if weapon.upgrades_map != None else 0
                        _has_upgrade = weapon.upgrades_map == None or _upgrade_map_index < len(value)
                        _has_money = _has_upgrade and self.player.money >= value[_upgrade_map_index]["price"]
                        _btn_upgrade.enable(_has_upgrade and _has_money)
                        
                        def btn_upgrade_hover(btn: Button, upgrade_steps = value, bar = _bar, key = key):
                            btn.default_on_hover(btn)
                            if btn.hovered:
                                match key:
                                    case "range":
                                        _step = self.range_bar.max_value / self.range_bar.bars_count
                                        bar.upgrade_value = (_step * upgrade_steps[0]["ammount"])/2
                                    case "concentration":
                                        _step = self.concentration_bar.max_value / self.concentration_bar.bars_count
                                        bar.upgrade_value = (_step * upgrade_steps[0]["ammount"])
                                    case _:
                                        bar.upgrade_value = upgrade_steps[0]["ammount"]
                                bar.rerender()
                            else:
                                bar.upgrade_value = 0
                                bar.rerender()
                            
                        _btn_upgrade.on_hover =btn_upgrade_hover
                        if _has_upgrade:
                            _upgrade_price_text = f'$ {value[_upgrade_map_index]["price"]:.2f}'
                        else:
                            _upgrade_price_text = "MAX"
                            _bar.upgrade_value = 0
                            
                        _txt_upgrade_price = menu_controller.get_text_surface(_upgrade_price_text, colors.WHITE if _has_money else colors.RED, resources.px_font(18))
                        _txt_upgrade_price_rect = _txt_upgrade_price.get_rect()
                        _txt_upgrade_price_rect.centery = _bar.rect.centery
                        _txt_upgrade_price_rect.left = _bar.rect.right + _btn_upgrade.rect.width + 5
                        pnl_right.blit(_txt_upgrade_price, _txt_upgrade_price_rect)
                else:
                    for b in _weapon_upgrade_btns:
                        b.visible = False
                    
                for b in _weapon_upgrade_btns:
                    b.draw(pnl_right, vec(0,0))
                    
                btn_sell_weapon = self.buttons[1]
                if btn_sell_weapon.rect.topleft == (0,0):
                    btn_sell_weapon.rect.left = self.panel_margin.x/2 + pnl_right_rect.left + 20
                    btn_sell_weapon.rect.bottom = self.panel_margin.y/2 + pnl_right_rect.top + pnl_right_rect.height - 20
                    btn_sell_weapon.set_pos(vec(btn_sell_weapon.rect.topleft))
                _btn_sell_text = f"Sell for $ {self.get_weapon_value(weapon)/2:.2f}"
                if btn_sell_weapon.text != _btn_sell_text:
                    btn_sell_weapon.set_text(_btn_sell_text)
                    btn_sell_weapon.on_hover(btn_sell_weapon)
                    
                btn_sell_weapon.draw(pnl_right, vec(-self.panel_margin.x/2 - pnl_right_rect.left, -self.panel_margin.y/2 - pnl_right_rect.top))
                
                pnl_right.blit(_txt_weapon_title, _txt_weapon_title_rect)
            
                self.damage_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_damage, _txt_damage_rect)
                
                self.firerate_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_firerate, _txt_firerate_rect)

                self.reload_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_reload_speed, _txt_reload_speed_rect)
                
                self.range_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_range, _txt_range_rect)

                self.magazine_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_magazine, _txt_magazine_rect)

                self.concentration_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_concentration, _txt_concentration_rect)
                
                self.stamina_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_stamina, _txt_stamina_rect)
                #endregion
                ...
                
            if self.selected_card.item_name == "backpack":
                _txt_item_title = menu_controller.get_text_surface("Backpack", colors.WHITE, resources.px_font(40))
                _txt_item_title_rect = _txt_item_title.get_rect()
                _txt_item_title_rect.top = 5
                _txt_item_title_rect.centerx = pnl_right_rect.width/2
                
                _lbls_margin = vec(5, 10)
                
                self.buttons[3].rect.left = self.panel_margin.x/2 + pnl_right_rect.left + 20
                self.buttons[3].rect.bottom = self.panel_margin.y/2 + pnl_right_rect.top + pnl_right_rect.height - 20
                self.buttons[3].set_pos(vec(self.buttons[3].rect.topleft))
                
                
                #icons
                if self.pistol_ammo_icon == None:
                    self.pistol_ammo_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\pistol_ammo_icon.png')
                    self.shotgun_ammo_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\shotgun_ammo_icon.png')
                    self.rifle_ammo_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\rifle_ammo_icon.png')
                    self.sniper_ammo_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\sniper_ammo_icon.png')
                    self.rocket_ammo_icon = pygame.image.load(f'{resources.IMAGES_PATH}ui\\rocket_ammo_icon.png')
                    
                    _icons = [self.pistol_ammo_icon, self.shotgun_ammo_icon, self.rifle_ammo_icon, self.sniper_ammo_icon, self.rocket_ammo_icon]
                    _max_size = max([max(i.get_size()) for i in _icons])
                    
                    _pistol_ratio = max(self.pistol_ammo_icon.get_size()) / _max_size
                    _shotgun_ratio = max(self.shotgun_ammo_icon.get_size()) / _max_size
                    _rifle_ratio = max(self.rifle_ammo_icon.get_size()) / _max_size
                    _sniper_ratio = max(self.sniper_ammo_icon.get_size()) / _max_size
                    _rocket_ratio = max(self.rocket_ammo_icon.get_size()) / _max_size
                    
                    self.pistol_ammo_icon = game_controller.scale_image(self.pistol_ammo_icon, (1 / _pistol_ratio) * 2.5, enums.ConvertType.CONVERT_ALPHA)
                    self.shotgun_ammo_icon = game_controller.scale_image(self.shotgun_ammo_icon, (1 / _shotgun_ratio) * 2.5, enums.ConvertType.CONVERT_ALPHA)
                    self.rifle_ammo_icon = game_controller.scale_image(self.rifle_ammo_icon, (1 / _rifle_ratio) * 2.5, enums.ConvertType.CONVERT_ALPHA)
                    self.sniper_ammo_icon = game_controller.scale_image(self.sniper_ammo_icon, (1 / _sniper_ratio) * 2.5, enums.ConvertType.CONVERT_ALPHA)
                    self.rocket_ammo_icon = game_controller.scale_image(self.rocket_ammo_icon, (1 / _rocket_ratio) * 2.5, enums.ConvertType.CONVERT_ALPHA)
                
                
                _icons = [self.pistol_ammo_icon, self.shotgun_ammo_icon, self.rifle_ammo_icon, self.sniper_ammo_icon, self.rocket_ammo_icon]
                _max_icon_width = max([i.get_width() for i in _icons])
                _bkp_upgrade_step = math.clamp(bkp.upgrade_step, 0, len(constants.ITEMS_UPGRADES['backpack'])-1)
                
                #region pistol ammo
                _pistol_icon_rect = self.pistol_ammo_icon.get_rect()
                _pistol_icon_rect.top = _txt_item_title_rect.bottom + 30
                _pistol_icon_rect.left = _lbls_margin.x *2
                
                _lbl_max_pistol = menu_controller.get_text_surface("Max pistol ammo:", colors.WHITE, resources.px_font(25))
                _lbl_max_pistol_rect = _lbl_max_pistol.get_rect()
                _lbl_max_pistol_rect.left = _max_icon_width + _lbls_margin.x*4
                _lbl_max_pistol_rect.centery = _pistol_icon_rect.centery
                
                _txt_max_pistol = menu_controller.get_text_surface(str(bkp.max_pistol_ammo), colors.LIGHT_BLUE, resources.px_font(25))
                _txt_max_pistol_rect = _txt_max_pistol.get_rect()
                _txt_max_pistol_rect.left = _lbl_max_pistol_rect.right + _lbls_margin.x
                _txt_max_pistol_rect.centery = _lbl_max_pistol_rect.centery
                
                _txt_pistol_upgrade = menu_controller.get_text_surface(f'+{constants.ITEMS_UPGRADES["backpack"][_bkp_upgrade_step]["max_pistol_ammo"]}', colors.GREEN, resources.px_font(22))
                _txt_pistol_upgrade_rect = _txt_pistol_upgrade.get_rect()
                _txt_pistol_upgrade_rect.left = _txt_max_pistol_rect.right + _lbls_margin.x
                _txt_pistol_upgrade_rect.centery = _txt_max_pistol_rect.centery
                #endregion
                
                #region shotgun ammo
                _shotgun_icon_rect = self.shotgun_ammo_icon.get_rect()
                _shotgun_icon_rect.top = _pistol_icon_rect.bottom + _lbls_margin.y
                _shotgun_icon_rect.centerx = _pistol_icon_rect.centerx
                
                _lbl_max_shotgun = menu_controller.get_text_surface("Max shotgun ammo:", colors.WHITE, resources.px_font(25))
                _lbl_max_shotgun_rect = _lbl_max_shotgun.get_rect()
                _lbl_max_shotgun_rect.left = _lbl_max_pistol_rect.left
                _lbl_max_shotgun_rect.centery = _shotgun_icon_rect.centery
                
                _txt_max_shotgun = menu_controller.get_text_surface(str(bkp.max_shotgun_ammo), colors.LIGHT_BLUE, resources.px_font(25))
                _txt_max_shotgun_rect = _txt_max_shotgun.get_rect()
                _txt_max_shotgun_rect.topleft = _lbl_max_shotgun_rect.topright + vec(_lbls_margin.x, 0)
                
                _txt_shotgun_upgrade = menu_controller.get_text_surface(f'+{constants.ITEMS_UPGRADES["backpack"][_bkp_upgrade_step]["max_shotgun_ammo"]}', colors.GREEN, resources.px_font(22))
                _txt_shotgun_upgrade_rect = _txt_shotgun_upgrade.get_rect()
                _txt_shotgun_upgrade_rect.left = _txt_max_shotgun_rect.right + _lbls_margin.x
                _txt_shotgun_upgrade_rect.centery = _txt_max_shotgun_rect.centery
                #endregion
                
                #region rifle ammo
                _rifle_icon_rect = self.rifle_ammo_icon.get_rect()
                _rifle_icon_rect.top = _shotgun_icon_rect.bottom + _lbls_margin.y
                _rifle_icon_rect.centerx = _shotgun_icon_rect.centerx
                
                _lbl_max_rifle = menu_controller.get_text_surface("Max rifle ammo:", colors.WHITE, resources.px_font(25))
                _lbl_max_rifle_rect = _lbl_max_rifle.get_rect()
                _lbl_max_rifle_rect.left = _lbl_max_pistol_rect.left
                _lbl_max_rifle_rect.centery = _rifle_icon_rect.centery
                
                _txt_max_rifle = menu_controller.get_text_surface(str(bkp.max_rifle_ammo), colors.LIGHT_BLUE, resources.px_font(25))
                _txt_max_rifle_rect = _txt_max_rifle.get_rect()
                _txt_max_rifle_rect.topleft = _lbl_max_rifle_rect.topright + vec(_lbls_margin.x, 0)
                
                _txt_rifle_upgrade = menu_controller.get_text_surface(f'+{constants.ITEMS_UPGRADES["backpack"][_bkp_upgrade_step]["max_rifle_ammo"]}', colors.GREEN, resources.px_font(22))
                _txt_rifle_upgrade_rect = _txt_rifle_upgrade.get_rect()
                _txt_rifle_upgrade_rect.left = _txt_max_rifle_rect.right + _lbls_margin.x
                _txt_rifle_upgrade_rect.centery = _txt_max_rifle_rect.centery
                #endregion
                
                #region sniper ammo
                _sniper_icon_rect = self.sniper_ammo_icon.get_rect()
                _sniper_icon_rect.top = _rifle_icon_rect.bottom + _lbls_margin.y
                _sniper_icon_rect.centerx = _rifle_icon_rect.centerx
                
                _lbl_max_sniper = menu_controller.get_text_surface("Max sniper ammo:", colors.WHITE, resources.px_font(25))
                _lbl_max_sniper_rect = _lbl_max_sniper.get_rect()
                _lbl_max_sniper_rect.left = _lbl_max_pistol_rect.left
                _lbl_max_sniper_rect.centery = _sniper_icon_rect.centery
                
                _txt_max_sniper = menu_controller.get_text_surface(str(bkp.max_sniper_ammo), colors.LIGHT_BLUE, resources.px_font(25))
                _txt_max_sniper_rect = _txt_max_sniper.get_rect()
                _txt_max_sniper_rect.topleft = _lbl_max_sniper_rect.topright + vec(_lbls_margin.x, 0)

                _txt_sniper_upgrade = menu_controller.get_text_surface(f'+{constants.ITEMS_UPGRADES["backpack"][_bkp_upgrade_step]["max_sniper_ammo"]}', colors.GREEN, resources.px_font(22))
                _txt_sniper_upgrade_rect = _txt_sniper_upgrade.get_rect()
                _txt_sniper_upgrade_rect.left = _txt_max_sniper_rect.right + _lbls_margin.x
                _txt_sniper_upgrade_rect.centery = _txt_max_sniper_rect.centery
                #endregion
                
                #region rocket ammo
                _rocket_icon_rect = self.rocket_ammo_icon.get_rect()
                _rocket_icon_rect.top = _sniper_icon_rect.bottom + _lbls_margin.y
                _rocket_icon_rect.centerx = _sniper_icon_rect.centerx
                
                _lbl_max_rocket = menu_controller.get_text_surface("Max rocket ammo:", colors.WHITE, resources.px_font(25))
                _lbl_max_rocket_rect = _lbl_max_rocket.get_rect()
                _lbl_max_rocket_rect.left = _lbl_max_pistol_rect.left
                _lbl_max_rocket_rect.centery = _rocket_icon_rect.centery
                
                _txt_max_rocket = menu_controller.get_text_surface(str(bkp.max_rocket_ammo), colors.LIGHT_BLUE, resources.px_font(25))
                _txt_max_rocket_rect = _txt_max_rocket.get_rect()
                _txt_max_rocket_rect.topleft = _lbl_max_rocket_rect.topright + vec(_lbls_margin.x, 0)

                _txt_rocket_upgrade = menu_controller.get_text_surface(f'+{constants.ITEMS_UPGRADES["backpack"][_bkp_upgrade_step]["max_rocket_ammo"]}', colors.GREEN, resources.px_font(22))
                _txt_rocket_upgrade_rect = _txt_rocket_upgrade.get_rect()
                _txt_rocket_upgrade_rect.left = _txt_max_rocket_rect.right + _lbls_margin.x
                _txt_rocket_upgrade_rect.centery = _txt_max_rocket_rect.centery
                #endregion
                
                
                _has_bkp_upgrade = bkp.upgrade_step < len(constants.ITEMS_UPGRADES["backpack"])
                _btn_upgrade_bkp = self.buttons[3]
                
                _now = datetime.datetime.now()
                if _btn_upgrade_bkp.hovered:
                    _elapsed = _now - self.start_time
                    _ms = _elapsed.microseconds/1000 - _elapsed.seconds/1000
                    _show = (_ms > 300)
                    if _show and _has_bkp_upgrade:
                        pnl_right.blit(_txt_pistol_upgrade, _txt_pistol_upgrade_rect)
                        pnl_right.blit(_txt_shotgun_upgrade, _txt_shotgun_upgrade_rect)
                        pnl_right.blit(_txt_rifle_upgrade, _txt_rifle_upgrade_rect)
                        pnl_right.blit(_txt_sniper_upgrade, _txt_sniper_upgrade_rect)
                        pnl_right.blit(_txt_rocket_upgrade, _txt_rocket_upgrade_rect)
                
                pnl_right.blit(_txt_item_title, _txt_item_title_rect)
                
                pnl_right.blit(self.pistol_ammo_icon, _pistol_icon_rect)
                pnl_right.blit(_lbl_max_pistol, _lbl_max_pistol_rect)
                pnl_right.blit(_txt_max_pistol, _txt_max_pistol_rect)
                
                pnl_right.blit(self.shotgun_ammo_icon, _shotgun_icon_rect)
                pnl_right.blit(_lbl_max_shotgun, _lbl_max_shotgun_rect)
                pnl_right.blit(_txt_max_shotgun, _txt_max_shotgun_rect)
                
                pnl_right.blit(self.rifle_ammo_icon, _rifle_icon_rect)
                pnl_right.blit(_lbl_max_rifle, _lbl_max_rifle_rect)
                pnl_right.blit(_txt_max_rifle, _txt_max_rifle_rect)
                
                pnl_right.blit(self.sniper_ammo_icon, _sniper_icon_rect)
                pnl_right.blit(_lbl_max_sniper, _lbl_max_sniper_rect)
                pnl_right.blit(_txt_max_sniper, _txt_max_sniper_rect)
                
                pnl_right.blit(self.rocket_ammo_icon, _rocket_icon_rect)
                pnl_right.blit(_lbl_max_rocket, _lbl_max_rocket_rect)
                pnl_right.blit(_txt_max_rocket, _txt_max_rocket_rect)
                
                _btn_upgrade_bkp.draw(pnl_right, vec(-self.panel_margin.x/2 - pnl_right_rect.left, -self.panel_margin.y/2 - pnl_right_rect.top))
            elif self.selected_card.item_name == "player":
                _txt_item_title = menu_controller.get_text_surface("Player", colors.WHITE, resources.px_font(40))
                _txt_item_title_rect = _txt_item_title.get_rect()
                _txt_item_title_rect.top = 5
                _txt_item_title_rect.centerx = pnl_right_rect.width/2
                
                _bar_pos = vec(10, _txt_item_title_rect.bottom + 10)
                _bars_margin = 10
                _bars_size = vec(pnl_right_rect.width/2,15)
                
                _max_health = self.player.max_health
                _movement_speed = self.player.start_movement_speed
                _sprint_speed = self.player.sprint_speed_weight
                _jump_force = self.player.jump_force
                _max_stamina = self.player.max_stamina
                _stamina_regen_rate = self.player.stamina_regen_rate
                _stamina_regen_haste = 5000 / self.player.stamina_regen_delay_ms
                _jump_stamina_skill = 100 / self.player.jump_stamina_drain
                _sprint_stamina_skill = 100 / self.player.sprint_stamina_drain
                _attack_stamina_skill = 10 / self.player.attack_stamina_drain
                
                #region Player bars
                
                if self.max_health_bar == None:
                    self.max_health_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*0), _bars_size), max_value = self.player_attributes_max["max_health"], value = _max_health, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.max_health_bar.value = _max_health
                    
                if self.movement_speed_bar == None:
                    self.movement_speed_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*1), _bars_size), max_value = self.player_attributes_max["movement_speed"], value = _movement_speed, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.movement_speed_bar.value = _movement_speed

                if self.sprint_speed_bar == None:
                    self.sprint_speed_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*2), _bars_size), max_value = self.player_attributes_max["sprint_speed"], value = _sprint_speed, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.sprint_speed_bar.value = _sprint_speed

                if self.jump_force_bar == None:
                    self.jump_force_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*3), _bars_size), max_value = self.player_attributes_max["jump_force"], value = _jump_force, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.jump_force_bar.value = _jump_force
                    
                if self.max_stamina_bar == None:
                    self.max_stamina_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*4), _bars_size), max_value = self.player_attributes_max["max_stamina"], value = _max_stamina, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.max_stamina_bar.value = _max_stamina

                if self.stamina_regen_rate_bar == None:
                    self.stamina_regen_rate_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*5), _bars_size), max_value = self.player_attributes_max["stamina_regen_rate"], value = _stamina_regen_rate, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.stamina_regen_rate_bar.value = _stamina_regen_rate

                if self.stamina_regen_haste_bar == None:
                    self.stamina_regen_haste_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*6), _bars_size), max_value = self.player_attributes_max["stamina_regen_haste"], value = _stamina_regen_haste, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.stamina_regen_haste_bar.value = _stamina_regen_haste

                if self.jump_stamina_skill_bar == None:
                    self.jump_stamina_skill_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*7), _bars_size), max_value = self.player_attributes_max["jump_stamina_skill"], value = _jump_stamina_skill, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.jump_stamina_skill_bar.value = _jump_stamina_skill

                if self.sprint_stamina_skill_bar == None:
                    self.sprint_stamina_skill_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*8), _bars_size), max_value = self.player_attributes_max["sprint_stamina_skill"], value = _sprint_stamina_skill, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.sprint_stamina_skill_bar.value = _sprint_stamina_skill

                if self.attack_stamina_skill_bar == None:
                    self.attack_stamina_skill_bar = AttributeBar(pygame.Rect(_bar_pos + vec(0,(_bars_size.y + _bars_margin)*9), _bars_size), max_value = self.player_attributes_max["attack_stamina_skill"], value = _attack_stamina_skill, **constants.ATTRIBUTE_BARS["weapon"])
                else:
                    self.attack_stamina_skill_bar.value = _attack_stamina_skill
                #endregion
                
                _lbls_margin = vec(5, 10)
                
                _txt_max_health = menu_controller.get_text_surface("Max health:", colors.WHITE, resources.px_font(25))
                _txt_max_health_rect = _txt_max_health.get_rect()
                _txt_max_health_rect.centery = self.max_health_bar.rect.centery
                _txt_max_health_rect.left = _bar_pos.x
                
                _txt_movement_speed = menu_controller.get_text_surface("Movement speed:", colors.WHITE, resources.px_font(25))
                _txt_movement_speed_rect = _txt_movement_speed.get_rect()
                _txt_movement_speed_rect.centery = self.movement_speed_bar.rect.centery
                _txt_movement_speed_rect.left = _bar_pos.x
                
                _txt_sprint_speed = menu_controller.get_text_surface("Sprint speed:", colors.WHITE, resources.px_font(25))
                _txt_sprint_speed_rect = _txt_sprint_speed.get_rect()
                _txt_sprint_speed_rect.centery = self.sprint_speed_bar.rect.centery
                _txt_sprint_speed_rect.left = _bar_pos.x
                
                _txt_jump_force = menu_controller.get_text_surface("Jump force:", colors.WHITE, resources.px_font(25))
                _txt_jump_force_rect = _txt_jump_force.get_rect()
                _txt_jump_force_rect.centery = self.jump_force_bar.rect.centery
                _txt_jump_force_rect.left = _bar_pos.x
                
                _txt_max_stamina = menu_controller.get_text_surface("Max stamina:", colors.WHITE, resources.px_font(25))
                _txt_max_stamina_rect = _txt_max_stamina.get_rect()
                _txt_max_stamina_rect.centery = self.max_stamina_bar.rect.centery
                _txt_max_stamina_rect.left = _bar_pos.x

                _txt_stamina_regen = menu_controller.get_text_surface("Stamina regen:", colors.WHITE, resources.px_font(25))
                _txt_stamina_regen_rect = _txt_stamina_regen.get_rect()
                _txt_stamina_regen_rect.centery = self.stamina_regen_rate_bar.rect.centery
                _txt_stamina_regen_rect.left = _bar_pos.x
                
                _txt_stamina_haste = menu_controller.get_text_surface("Stamina haste:", colors.WHITE, resources.px_font(25))
                _txt_stamina_haste_rect = _txt_stamina_haste.get_rect()
                _txt_stamina_haste_rect.centery = self.stamina_regen_haste_bar.rect.centery
                _txt_stamina_haste_rect.left = _bar_pos.x
                
                _txt_jump_stamina = menu_controller.get_text_surface("Jump stamina:", colors.WHITE, resources.px_font(25))
                _txt_jump_stamina_rect = _txt_jump_stamina.get_rect()
                _txt_jump_stamina_rect.centery = self.jump_stamina_skill_bar.rect.centery
                _txt_jump_stamina_rect.left = _bar_pos.x

                _txt_sprint_stamina = menu_controller.get_text_surface("Sprint stamina:", colors.WHITE, resources.px_font(25))
                _txt_sprint_stamina_rect = _txt_sprint_stamina.get_rect()
                _txt_sprint_stamina_rect.centery = self.sprint_stamina_skill_bar.rect.centery
                _txt_sprint_stamina_rect.left = _bar_pos.x

                _txt_attack_stamina = menu_controller.get_text_surface("Attack stamina:", colors.WHITE, resources.px_font(25))
                _txt_attack_stamina_rect = _txt_attack_stamina.get_rect()
                _txt_attack_stamina_rect.centery = self.attack_stamina_skill_bar.rect.centery
                _txt_attack_stamina_rect.left = _bar_pos.x
                
                _max_txt_width = max([x.width for x in [_txt_max_health_rect, _txt_movement_speed_rect, _txt_sprint_speed_rect, _txt_jump_force_rect, _txt_max_stamina_rect, _txt_stamina_regen_rect, _txt_stamina_haste_rect, _txt_jump_stamina_rect, _txt_sprint_stamina_rect, _txt_attack_stamina_rect]])
                _txt_left = _txt_max_health_rect.left + _max_txt_width + _bars_margin/2
                self.max_health_bar.rect.left = _txt_left
                self.movement_speed_bar.rect.left = _txt_left
                self.sprint_speed_bar.rect.left = _txt_left
                self.jump_force_bar.rect.left = _txt_left
                self.max_stamina_bar.rect.left = _txt_left
                self.stamina_regen_rate_bar.rect.left = _txt_left
                self.stamina_regen_haste_bar.rect.left = _txt_left
                self.jump_stamina_skill_bar.rect.left = _txt_left
                self.sprint_stamina_skill_bar.rect.left = _txt_left
                self.attack_stamina_skill_bar.rect.left = _txt_left
                
                _attribute_bars = {
                    "max_health": self.max_health_bar,
                    "movement_speed": self.movement_speed_bar,
                    "sprint_speed": self.sprint_speed_bar,
                    "jump_force": self.jump_force_bar,
                    "max_stamina": self.max_stamina_bar,
                    "stamina_regen_rate": self.stamina_regen_rate_bar,
                    "stamina_regen_haste": self.stamina_regen_haste_bar,
                    "jump_stamina_skill": self.jump_stamina_skill_bar,
                    "sprint_stamina_skill": self.sprint_stamina_skill_bar,
                    "attack_stamina_skill": self.attack_stamina_skill_bar
                }
                
                for b in _attribute_bars.values():
                    if b.value == 0:
                        b.bar_border_color = colors.DARK_GRAY
                    else:
                        b.bar_border_color = b.start_bar_border_color
                
                _player_upgrades = constants.get_player_upgrade(self.player.character)
                if _player_upgrades != None:
                    _unused_btns = [b for b in _player_upgrade_btns if b.name not in _player_upgrades.keys()]
                    for b in _unused_btns:
                        b.visible = False
                    
                    for key, value in _player_upgrades.items():
                        _btn_upgrade = [b for b in _player_upgrade_btns if key in b.name]
                        _bar = _attribute_bars[key]
                        if len(_btn_upgrade) <= 0 or _bar == None:
                            continue
                        _btn_upgrade = _btn_upgrade[0]
                        _btn_upgrade.rect.left = _bar.rect.right + self.panel_margin.x/2 + pnl_right_rect.left
                        _btn_upgrade.rect.centery = _bar.rect.centery + self.panel_margin.y/2 + pnl_right_rect.top
                        _btn_upgrade.visible = True
                        _btn_upgrade.on_click = lambda attr_name = key: self.buy_player_upgrade(self.player.character, attr_name)
                        _upgrade_map_index = math.clamp(self.player.upgrades_map[key], 0, len(value)) if self.player.upgrades_map != None else 0
                        _has_upgrade = self.player.upgrades_map == None or _upgrade_map_index < len(value)
                        _has_money = _has_upgrade and self.player.money >= value[_upgrade_map_index]["price"]
                        _btn_upgrade.enable(_has_upgrade and _has_money)
                        
                        def btn_upgrade_hover(btn: Button, upgrade_steps = value, bar = _bar, key = key):
                            btn.default_on_hover(btn)
                            if btn.hovered:
                                bar.upgrade_value = upgrade_steps[0]["ammount"]
                                bar.rerender()
                            else:
                                bar.upgrade_value = 0
                                bar.rerender()
                            
                        _btn_upgrade.on_hover =btn_upgrade_hover
                        if _has_upgrade:
                            _upgrade_price_text = f'$ {value[_upgrade_map_index]["price"]:.2f}'
                        else:
                            _upgrade_price_text = "MAX"
                            _bar.upgrade_value = 0
                            
                        _txt_upgrade_price = menu_controller.get_text_surface(_upgrade_price_text, colors.WHITE if _has_money else colors.RED, resources.px_font(18))
                        _txt_upgrade_price_rect = _txt_upgrade_price.get_rect()
                        _txt_upgrade_price_rect.centery = _bar.rect.centery
                        _txt_upgrade_price_rect.left = _bar.rect.right + _btn_upgrade.rect.width + 5
                        pnl_right.blit(_txt_upgrade_price, _txt_upgrade_price_rect)
                else:
                    for b in _player_upgrade_btns:
                        b.visible = False
                    
                for b in _player_upgrade_btns:
                    b.draw(pnl_right, vec(0,0))
                
                pnl_right.blit(_txt_item_title, _txt_item_title_rect)
                
                self.max_health_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_max_health, _txt_max_health_rect)
                
                self.movement_speed_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_movement_speed, _txt_movement_speed_rect)
                
                self.sprint_speed_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_sprint_speed, _txt_sprint_speed_rect)

                self.jump_force_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_jump_force, _txt_jump_force_rect)

                self.max_stamina_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_max_stamina, _txt_max_stamina_rect)

                self.stamina_regen_rate_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_stamina_regen, _txt_stamina_regen_rect)

                self.stamina_regen_haste_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_stamina_haste, _txt_stamina_haste_rect)

                self.jump_stamina_skill_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_jump_stamina, _txt_jump_stamina_rect)

                self.sprint_stamina_skill_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_sprint_stamina, _txt_sprint_stamina_rect)

                self.attack_stamina_skill_bar.draw(pnl_right, vec(0,0))
                pnl_right.blit(_txt_attack_stamina, _txt_attack_stamina_rect)
        else:
            for b in _player_upgrade_btns:
                b.visible = False
        
        
        self.image.blit(pnl_right, pnl_right_rect.topleft)
        
        pnl_btns = ["sell_weapon", "swap_slots"]
        for b in [b for b in self.buttons if not b.name.startswith("equip") and b.name not in pnl_btns]:
            b.draw(self.image, -self.panel_margin/2)

        #scroll bars
        self.inv_v_scrollbar.draw(self.image, - self.panel_margin/2)

        screen.blit(self.image, image_rect)
        
        
    def get_weapon_or_default(self, weapon_type: enums.Weapons):
        w = self.player.backpack.get_weapon(weapon_type)
        if w != None:
            return w
        
        return constants.get_weapon(weapon_type, vec(0,0), load_content = False)
    
    def upgrade_backpack(self):
        bkp = self.player.backpack
        step = constants.ITEMS_UPGRADES["backpack"][bkp.upgrade_step]
        
        if self.player.money < step["price"]:
            return
        
        bkp.max_pistol_ammo += step["max_pistol_ammo"]
        bkp.max_shotgun_ammo += step["max_shotgun_ammo"]
        bkp.max_rifle_ammo += step["max_rifle_ammo"]
        bkp.max_sniper_ammo += step["max_sniper_ammo"]
        bkp.max_rocket_ammo += step["max_rocket_ammo"]
        
        bkp.upgrade_step += 1
        self.purchase_sound.play()
        self.player.money -= step['price']
        menu_controller.popup(Popup(f"-${step['price']:.2f}", vec(self.money_rect.topleft), **constants.POPUPS["damage"]))
        
    def equip_weapon(self, weapon_type: enums.Weapons, as_primary = False):
        bkp = self.player.backpack
        
        #weapon already equipped and has only one (trying to be weaponless)
        if (bkp.equipped_primary == weapon_type or bkp.equipped_secondary == weapon_type) and type(bkp.equipped_primary) != type(bkp.equipped_secondary):
            menu_controller.popup(Popup(f"You cannot be unarmed!", vec(0,0), name="unarmed_error", unique=True, **constants.POPUPS["error"]), center=True)
            return
        
        if bkp.equipped_primary == weapon_type:
            self.player.change_weapon()
            bkp.equipped_primary = None
            return
        elif bkp.equipped_secondary == weapon_type:
            self.player.change_weapon()
            bkp.equipped_secondary = None
            return
            
        self.player.current_weapon = bkp.equip_weapon(weapon_type, as_primary)
        
    def buy_weapon_upgrade(self, weapon_type: enums.Weapons, attr_name):
        
        bpk = self.player.backpack
        weapon = bpk.get_weapon(weapon_type)
        attributes_dict = constants.get_weapon_upgrade(weapon_type)
        
        if weapon.upgrades_map == None:
            weapon.upgrades_map = constants.get_weapon_upgrade(weapon_type).copy()
            for key in weapon.upgrades_map.keys():
                weapon.upgrades_map[key] = 0
                
        price = attributes_dict[attr_name][weapon.upgrades_map[attr_name]]["price"]
        
        if price > self.player.money:
            return
        
        ammount = attributes_dict[attr_name][weapon.upgrades_map[attr_name]]["ammount"]
        weapon.upgrades_map[attr_name] += 1
        
        self.purchase_sound.play()
        self.player.money -= price
        menu_controller.popup(Popup(f"-${price:.2f}", vec(self.money_rect.topleft), **constants.POPUPS["damage"]))
        
        
        
        match attr_name:
            case "damage":
                match weapon.bullet_type:
                    case enums.BulletType.SHOTGUN:
                        weapon.damage += ammount / weapon.ballin_count
                    case _:
                        weapon.damage += ammount
            case "firerate":
                weapon.fire_rate += ammount
            case "reload_speed":
                match weapon.reload_type:
                    case enums.ReloadType.SINGLE_BULLET:
                        _new_value = self.reload_bar.value + ammount
                        weapon.reload_delay_ms = 5000 / (_new_value * weapon.magazine_size)
                    case _:
                        weapon.reload_delay_ms = 5000 / (self.reload_bar.value + ammount)
            case "range":
                _step = self.range_bar.max_value / self.range_bar.bars_count
                
                weapon.bullet_min_range += _step * ammount/2
                weapon.bullet_max_range += _step * ammount/2
            case "concentration":
                weapon.dispersion = 90 / (self.concentration_bar.value + ammount)
            case "magazine_size":
                weapon.magazine_size += ammount
            case "stamina":
                weapon.stamina_use = 6 / (self.stamina_bar.value + ammount)
                
    def buy_player_upgrade(self, character_name: enums.Characters, attr_name):
        
        p = self.player
        attributes_dict = constants.get_player_upgrade(character_name)
        
        if p.upgrades_map == None:
            p.upgrades_map = constants.get_player_upgrade(character_name).copy()
            for key in p.upgrades_map.keys():
                p.upgrades_map[key] = 0
                
        price = attributes_dict[attr_name][p.upgrades_map[attr_name]]["price"]
        
        if price > self.player.money:
            return
        
        ammount = attributes_dict[attr_name][p.upgrades_map[attr_name]]["ammount"]
        p.upgrades_map[attr_name] += 1
        
        self.purchase_sound.play()
        self.player.money -= price
        menu_controller.popup(Popup(f"-${price:.2f}", vec(self.money_rect.topleft), **constants.POPUPS["damage"]))
        
        match attr_name:
            case "max_health":
                p.max_health += ammount
                p.health_bar.set_max_value(p.max_health)
            case "movement_speed":
                p.start_movement_speed += ammount
            case "sprint_speed":
                p.sprint_speed_weight += ammount
                p.sprint_speed_multiplier = (p.sprint_speed_weight*0.7) / p.movement_speed
            case "jump_force":
                p.jump_force += ammount
            case "max_stamina":
                p.max_stamina += ammount
                p.stamina_bar.set_max_value(p.max_stamina)
            case "stamina_regen_rate":
                p.stamina_regen_rate += ammount
                
            case "stamina_regen_haste":
                p.stamina_regen_delay_ms = 5000 / (self.stamina_regen_haste_bar.value + ammount)
            case "jump_stamina_skill":
                p.jump_stamina_drain = 100 / (self.jump_stamina_skill_bar.value + ammount)
            case "sprint_stamina_skill":
                p.sprint_stamina_drain = 100 / (self.sprint_stamina_skill_bar.value + ammount)
            case "attack_stamina_skill":
                p.attack_stamina_drain = 10 / (self.attack_stamina_skill_bar.value + ammount)
                
    def swap_weapon_slots(self):
        bkp = self.player.backpack
        
        w1 = bkp.get_weapon(bkp.equipped_primary)
        w2 = bkp.get_weapon(bkp.equipped_secondary)
        
        #primary cannot fit in secondary slot
        if (w1!=None and w1.is_primary) or (w2!=None and w2.is_primary):
            _pop_dict = constants.POPUPS["error"].copy()
            _pop_dict.pop("font")
            _popup = Popup(f"Can only swap secondaries!", self.buttons[2].rect.topleft, name="primary_2_error", unique=True, **_pop_dict, font = resources.px_font(15))
            _popup.rect.centerx = self.buttons[2].rect.centerx
            _popup.rect.bottom = self.buttons[2].rect.top
            menu_controller.popup(_popup)
            return
        
        bkp.equipped_primary = w2.weapon_type if w2 != None else None
        bkp.equipped_secondary = w1.weapon_type if w1 != None else None
                
    def get_weapon_value(self, weapon: Weapon):
        value = weapon.purchase_price
        
        if weapon.upgrades_dict == None or weapon.upgrades_map == None:
            return value
        
        for up_name in weapon.upgrades_dict.keys():
            for i, step in enumerate(weapon.upgrades_dict[up_name]):
                if i > weapon.upgrades_map[up_name]-1:
                    continue
                value += step["price"]
        
        return value
                
    def sell_weapon(self, weapon_type: enums.Weapons):
        
        bkp = self.player.backpack
        weapon = bkp.get_weapon(weapon_type)
        if weapon == None:
            return
        
    
        #if it's equiped
        if (weapon_type == bkp.equipped_primary or weapon_type == bkp.equipped_secondary):
            #if it's the only equiped
            if type(bkp.equipped_primary) != type(bkp.equipped_secondary):
                _weapons = [*bkp.primary_weapons, *bkp.secondary_weapons]
                if weapon in _weapons:
                    _weapons.remove(weapon)
                #if there's no more weapon to equip
                if len(_weapons) <= 0:
                    menu_controller.popup(Popup(f"You cannot be unarmed!", vec(0,0), name="unarmed_error", unique=True, **constants.POPUPS["error"]), center=True)
                    return
        
        if weapon_type == bkp.equipped_primary:
            bkp.equipped_primary = None
        elif weapon_type == bkp.equipped_secondary:
            bkp.equipped_secondary = None
        
        if weapon.is_primary:
            bkp.primary_weapons.remove(weapon)
        else:
            bkp.secondary_weapons.remove(weapon)
            
        
            
        if bkp.equipped_primary == None and bkp.equipped_secondary == None:
            _weapons = [*bkp.primary_weapons, *bkp.secondary_weapons]
            self.player.current_weapon = bkp.equip_weapon(_weapons[0].weapon_type)

        sell_price = self.get_weapon_value(weapon)/2
        self.player.money += sell_price
        
        menu_controller.popup(Popup(f"+${sell_price:.2f}", vec(self.money_rect.topleft), **constants.POPUPS["health"]))
        self.selected_card = None
        self.selected_weapon = None
        self.purchase_sound.play()
        self.load_inventory()