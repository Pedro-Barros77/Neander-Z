import pygame, os
from pygame.math import Vector2 as vec

from domain.models.ui.text_input import TextInput
from domain.models.ui.pages.page import Page
from domain.models.ui.button import Button
from domain.models.ui.popup_text import Popup
from domain.utils import constants, colors, enums
from domain.services import menu_controller, game_controller
from domain.engine.game import Game

class NewGame(Page):
    def __init__(self, screen: pygame.Surface, **kwargs) -> None:
        super().__init__("NewGame" ,**kwargs)
        
        self.screen: pygame.Surface = screen
        
        btn_dict = {
            "text_font": pygame.font.Font(f'{constants.FONTS_PATH}runescape_uf.ttf', 30),
            "text_color": colors.BLACK
        }
        
        self.buttons.extend([
            Button(vec(0,250), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Single Player", on_click = lambda: self.start_game(enums.ClientType.SINGLE),**btn_dict),
            Button(vec(0,395), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Host Game", on_click = lambda: self.start_game(enums.ClientType.HOST),**btn_dict),
            Button(vec(0,455), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Enter Game", on_click = lambda: self.start_game(enums.ClientType.GUEST),**btn_dict),
            # Button(vec(0,515), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "teste", on_click = self.teste,**btn_dict)
        ])

        
        for b in self.buttons:
            b.rect.centerx = self.screen.get_rect().centerx
            b.center = (b.rect.centerx, b.rect.centery)
            
        return_page = lambda: menu_controller.pages_history.pop()
        self.buttons.append(Button(vec(30,self.screen.get_height() - 100), f'{constants.IMAGES_PATH}ui\\btn_return.png', scale = 2, on_click = return_page,**btn_dict))
        
        self.btn_panel, self.btn_panel_rect = self.create_panel()
        
        self.line_divider = pygame.Surface((self.btn_panel_rect.width, 1))
        self.line_divider_rect = pygame.Rect((self.btn_panel_rect.left, self.buttons[0].rect.bottom + 20), (self.line_divider.get_size()))
        self.line_divider.fill(colors.WHITE)
        
        self.txt_ip_input = TextInput(
            pygame.Rect((self.buttons[0].rect.left, self.line_divider_rect.top + 20), (self.buttons[0].rect.width*0.6,30)),
            font = pygame.font.Font(constants.PIXEL_FONT, 22),
            font_color = colors.BLACK,
            background_color = colors.WHITE,
            border_color = colors.LIGHT_GRAY,
            border_width = 2,
            cursor_color = colors.BLACK,
            padding = (5,5),
            place_holder="IP Address",
            place_holder_color = colors.LIGHT_GRAY)
        
        self.txt_port_input = self.txt_ip_input.from_this_template(
            pygame.Rect((self.txt_ip_input.rect.left + self.txt_ip_input.rect.width + self.buttons[0].rect.width*0.1, self.line_divider_rect.top + 20),(self.buttons[0].rect.width*0.3,30)),
            place_holder="Port"
        )
        
        self.txt_ip_input.set_buffer([menu_controller.config_state['ip']])
        self.txt_port_input.set_buffer([menu_controller.config_state['port']])
        
        self.logo_frames: list[pygame.sprite.Sprite] = game_controller.load_sprites(f'{constants.IMAGES_PATH}ui\\logo_anim\\')
        self.logo_scale = 0.5
        self.logo_frame = 0
        self.logo_image: pygame.Surface = None
        
        self.set_background(f'{constants.IMAGES_PATH}ui\\bg_main_menu.png')
        
    
    def teste(self):
        print('teste')
        
    def update(self, **kwargs):
        events = kwargs.pop("events", None)
        
        self.logo_anim(0.1)
        self.txt_ip_input.update(events)
        self.txt_port_input.update(events)
        
        
    
        return super().update(**kwargs)
    
    def draw(self):
        # background
        if self.background_image != None:
            self.screen.blit(self.background_image, (0,0))
            
        # btn panel
        self.screen.blit(self.btn_panel, self.btn_panel_rect)
        
        #logo
        _logo_rect = self.logo_image.get_rect()
        _logo_rect.centerx = self.background_image.get_width()/2
        _logo_rect.top = 10
        self.screen.blit(self.logo_image, _logo_rect)
        
        #line divider
        self.screen.blit(self.line_divider, self.line_divider_rect)
        
        #ip input:
        self.txt_ip_input.draw(self.screen)
        self.txt_port_input.draw(self.screen)
        
        super().draw()
        
        
        
    def start_game(self, client_type: enums.ClientType):
        ip = self.txt_ip_input.get_value()
        port = self.txt_port_input.get_value()
        
        if client_type != enums.ClientType.SINGLE and len(ip) + len(port) > 0:
            if len(ip) > 0:
                menu_controller.config_state["ip"] = ip
            if len(port) > 0:
                menu_controller.config_state["port"] = port
            menu_controller.save_states([menu_controller.config_state])
            
            
        game = Game(client_type, self.screen)
        game.setup()
        
        match client_type:
            case enums.ClientType.SINGLE:
                ...
            
            case enums.ClientType.HOST:
                menu_controller.playing = True
                game_controller.host_game(game, ip, int(port))
                
            case enums.ClientType.GUEST:
                menu_controller.playing = True
                succeeded = game_controller.try_enter_game(game, ip, int(port), timeout=0.3)
                if not succeeded:
                    menu_controller.popup(Popup("Cannot connect to host!", vec(self.screen.get_rect().center),
                        **constants.POPUPS["error"]
                        , name = "can't connect to host", unique = True
                        ), center=True)
                    menu_controller.playing = False
                    return
        menu_controller.pages_history.append(game)
        
                
        
    def logo_anim(self, speed: float):
        if self.logo_frame > len(self.logo_frames)-1:
            self.logo_frame = 0
        
        self.logo_image = game_controller.scale_image(self.logo_frames[int(self.logo_frame)], self.logo_scale)
        self.logo_frame += speed
             
    def create_panel(self):
        _padding = vec(80,15)
        _transparency = 127.5
        
        
        btn_panel_rect = self.buttons[0].rect.copy()
        btn_panel_rect.width += _padding.x
        btn_panel_rect.height = (btn_panel_rect.height + _padding.y) * len(self.buttons)
        btn_panel_rect.center = vec(self.buttons[0].rect.width/2, sum([b.rect.height for b in self.buttons])/2) + vec(self.buttons[0].rect.topleft)
        btn_panel = pygame.Surface(btn_panel_rect.size, pygame.SRCALPHA)
        btn_panel = btn_panel.convert_alpha()
        btn_panel.fill((0,0,0,_transparency))
        
        return btn_panel, btn_panel_rect