import pygame
from pygame.math import Vector2 as vec

from domain.services import menu_controller, resources
from domain.utils import colors, constants
from domain.models.ui.button import Button
from domain.models.ui.pages.modals.modal import Modal

class Pause(Modal):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)

        self.active = False

        
        
        self.game = game
        btn_dict = {
            "text_font": resources.px_font(30),
            "text_color": colors.BLACK
        }

        self.buttons: list[Button] = []
        self.buttons.extend([
            Button(vec(0, self.panel_margin.y + 200), f'{resources.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Continue", on_click = self.hide ,**btn_dict),
            Button(vec(0, self.panel_margin.y + 260), f'{resources.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Restart", on_click = self.game.restart_game,**btn_dict),
            Button(vec(0, self.panel_margin.y + 320), f'{resources.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Main Menu", on_click = self.main_menu,**btn_dict),
        ])
        
        for b in self.buttons:
            b.rect.centerx = self.game.screen.get_rect().centerx
            b.center = (b.rect.centerx, b.rect.centery)
    
    def main_menu(self):
        pygame.mixer.music.stop()
        menu_controller.pages_history = menu_controller.pages_history[:1]
        
    def show(self):
        self.game.focused = False
        self.active = True
        pygame.mixer.music.pause()
        
    def hide(self):
        self.active = False
        self.game.focused = True
        pygame.mixer.music.unpause()
    
    def set_tab(self, i: int):
        self.tab_index = i
        match i:
            case 0:
                self.buttons[0].enable(False)
                self.buttons[1].enable(True)
            case 1:
                self.buttons[0].enable(True)
                self.buttons[1].enable(False)
    
    def draw(self, screen: pygame.Surface):
        #black panel
        super().draw(screen)
        
        screen_rect = screen.get_rect()
        
        pause_title = menu_controller.get_text_surface("Game Paused", colors.WHITE, resources.px_font(80))        
        title_rect = pause_title.get_rect()
        title_rect.centerx = screen_rect.centerx
        title_rect.top = self.panel_margin.y + 30
        
        screen.blit(pause_title, title_rect)
        
        for b in self.buttons:
            b.draw(screen)


    def update(self):
        super().update()
        
        for b in self.buttons:
            b.update()
            
    def blit_debug(self, screen, **kwargs):
        pass