import pygame
from pygame.math import Vector2 as vec

from domain.models.ui.pages.page import Page
from domain.models.ui.pages.new_game import NewGame
from domain.models.ui.button import Button
from domain.utils import constants, colors
from domain.services import menu_controller, game_controller

class MainMenu(Page):
    def __init__(self, **kwargs) -> None:
        super().__init__("MainMenu", **kwargs)
        
        menu_controller.load_all_states()
        
        pygame.init()
        
        self.monitor_size: vec = vec(900, 600)
        self.screen: pygame.Surface = pygame.display.set_mode(self.monitor_size)

        
        btn_dict = {
            "text_font": pygame.font.Font(constants.PIXEL_FONT, 30),
            "text_color": colors.BLACK
        }
        
        self.buttons.extend([
            Button(vec(0,250), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Play",on_click = self.open_new_game,**btn_dict),
            Button(vec(0,310), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Options", **btn_dict),
            Button(vec(0,370), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Quit",on_click = lambda: menu_controller.quit_app(), **btn_dict),
        ])
        
        for b in self.buttons:
            b.rect.centerx = self.screen.get_rect().centerx
            b.center = (b.rect.centerx, b.rect.centery)
        
        self.btn_panel, self.btn_panel_rect = self.create_panel()
        
        self.logo_frames: list[pygame.sprite.Sprite] = game_controller.load_sprites(f'{constants.IMAGES_PATH}ui\\logo_anim\\')
        self.logo_scale = 0.5
        self.logo_frame = 0
        self.logo_image: pygame.Surface = None
        
        self.set_background(f'{constants.IMAGES_PATH}ui\\bg_main_menu.png')
        
        
    def open_new_game(self):
        new_game = NewGame(self.screen)
        menu_controller.pages_history.append(new_game)
        
    def update(self, **kwargs):
        self.logo_anim(0.1)
    
        return super().update(**kwargs)
    
    def draw(self):
        # drawing
        if self.background_image != None:
            self.screen.blit(self.background_image, (0,0))
            
        self.screen.blit(self.btn_panel, self.btn_panel_rect)
        
        _logo_rect = self.logo_image.get_rect()
        _logo_rect.centerx = self.background_image.get_width()/2
        _logo_rect.top = 10
        self.screen.blit(self.logo_image, _logo_rect)
        
        return super().draw()
        
    def logo_anim(self, speed: float):
        if self.logo_frame > len(self.logo_frames)-1:
            self.logo_frame = 0
        
        self.logo_image = game_controller.scale_image(self.logo_frames[int(self.logo_frame)], self.logo_scale)
        self.logo_frame += speed
    
    def create_panel(self):
        _padding = vec(80,20)
        _transparency = 127.5
        
        
        btn_panel_rect = self.buttons[0].rect.copy()
        btn_panel_rect.width += _padding.x
        btn_panel_rect.height = (btn_panel_rect.height + _padding.y) * len(self.buttons)
        btn_panel_rect.center = vec(self.buttons[0].rect.width/2, sum([b.rect.height for b in self.buttons])/2) + vec(self.buttons[0].rect.topleft)
        btn_panel = pygame.Surface(btn_panel_rect.size, pygame.SRCALPHA)
        btn_panel = btn_panel.convert_alpha()
        btn_panel.fill((0,0,0,_transparency))
        
        return btn_panel, btn_panel_rect