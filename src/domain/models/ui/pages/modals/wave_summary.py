import pygame
from pygame.math import Vector2 as vec

from domain.models.wave_result import WaveResult
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants
from domain.models.ui.button import Button

class WaveSummary:
    def __init__(self, results: tuple[WaveResult, WaveResult], **kwargs) -> None:
        self.buttons: list[Button] = []

        self.P1_RESULT = results[0]
        self.P2_RESULT = results[1]
    
        

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def draw(self, screen: pygame.Surface):
        screen_rect = screen.get_rect()
        self.screen = screen

        

        #margin from black panel to screen borders
        _panel_margin = vec(50,50)
        #distance between head icons and character names
        _icon_margin = vec(10, 0)
        #distance between players panels
        _player_panels_margin = vec(30, 0)
        
        panel = pygame.Surface(vec(screen_rect.size) - _panel_margin, pygame.SRCALPHA)
        panel.fill(colors.set_alpha(colors.BLACK, 200))

        #region Create button
        btn_dict = {
            "text_font": pygame.font.Font(f'{constants.FONTS_PATH}runescape_uf.ttf', 30),
            "text_color": colors.BLACK
        }

        _button_result_pos = _panel_margin[0] - 40
        _button_loja_pos = _button_result_pos + 210
        _button_ready_pos = _button_loja_pos  + 210
        
        self.buttons.extend([
            Button(vec(_button_result_pos, 480), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Result", on_click = lambda: print("result") ,**btn_dict),
            Button(vec(_button_loja_pos, 480), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Loja", on_click = lambda: print("loja"),**btn_dict),
            Button(vec(_button_ready_pos, 480), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Ready", on_click = lambda: print("ready"),**btn_dict)
        ])

        
        for b in self.buttons:
            b.on_click = lambda: print("teste")
            
            b.draw(panel)
                
        #endregion Create button

       
        wave_title = menu_controller.get_text_surface(f'Survived Wave {self.P1_RESULT.wave_number}', colors.RED, self.font(80))
        p1_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.P1_RESULT.player_character.value}\\head_icon.png'), 4)
        p1_title = menu_controller.get_text_surface(self.P1_RESULT.player_character.value, colors.WHITE, self.font(60))
        p2_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.P2_RESULT.player_character.value}\\head_icon.png'), 4)
        p2_title = menu_controller.get_text_surface(self.P2_RESULT.player_character.value, colors.WHITE, self.font(60))

        lbl_score = menu_controller.get_text_surface("wave score:", colors.WHITE, self.font(28))
        lbl_money = menu_controller.get_text_surface("earned money:", colors.WHITE, self.font(28))
        lbl_kills = menu_controller.get_text_surface("total kills:", colors.WHITE, self.font(28))
        
        p1_score = menu_controller.get_text_surface(str(self.P1_RESULT.score), colors.YELLOW, self.font(22))
        p1_money = menu_controller.get_text_surface(f'$ {self.P1_RESULT.money:.2f}', colors.GREEN, self.font(22))
        p1_kills = menu_controller.get_text_surface(str(self.P1_RESULT.kills_count), colors.RED, self.font(22))
        
        p2_score = menu_controller.get_text_surface(str(self.P2_RESULT.score), colors.YELLOW, self.font(22))
        p2_money = menu_controller.get_text_surface(f'$ {self.P2_RESULT.money:.2f}', colors.GREEN, self.font(22))
        p2_kills = menu_controller.get_text_surface(str(self.P2_RESULT.kills_count), colors.RED, self.font(22))

        labels = [lbl_score, lbl_money, lbl_kills]
        p1_values = [p1_score, p1_money, p1_kills]
        p2_values = [p2_score, p2_money, p2_kills]
        
        p1_surface = pygame.Surface((p1_icon.get_width() + p1_title.get_width() + 10, p1_icon.get_height() + 200), pygame.SRCALPHA)
        p1_surface.fill((0,0,0,0))
        pygame.draw.rect(p1_surface, colors.GREEN, p1_surface.get_rect(),3)

        p2_surface = pygame.Surface((p2_icon.get_width() + p2_title.get_width() + 10, p2_icon.get_height() + 200), pygame.SRCALPHA)
        p2_surface.fill((0,0,0,0))
        pygame.draw.rect(p2_surface, colors.GREEN, p2_surface.get_rect(),3)
        
        labels_surface = pygame.Surface(vec(screen_rect.width - _panel_margin.x - _player_panels_margin.x - _panel_margin.x/2 - (_player_panels_margin.x*2),200), pygame.SRCALPHA)
        labels_surface.fill((0,0,0,0))
        pygame.draw.rect(labels_surface, colors.GREEN, labels_surface.get_rect(),3)
        
        p2_surface.blit(p2_icon, (0,0))
        p2_surface.blit(p2_title, (p2_icon.get_width() + _icon_margin.x, 0))
        p1_surface.blit(p1_icon, (0,0))
        p1_surface.blit(p1_title, (p1_icon.get_width() + _icon_margin.x, 0))
        
        
        def draw_line(pos:vec, size:int):
            pygame.draw.line(labels_surface, colors.WHITE, pos, pos + vec(size,0), 1)
        
        lbl_margin = vec(10, 40)
        for i, l in enumerate(labels, start=1):
            _lbl_pos = vec(lbl_margin.x, lbl_margin.y * i)
            labels_surface.blit(l, _lbl_pos)
            draw_line(_lbl_pos + vec(0, l.get_height()), labels_surface.get_width())
            p1_surface.blit(p1_values[i-1], (10, _lbl_pos.y + p1_icon.get_height()))
            p2_surface.blit(p2_values[i-1], (10, _lbl_pos.y + p1_icon.get_height()))


        

        
        
        #black panel
        screen.blit(panel, _panel_margin/2)
        #wave title
        screen.blit(wave_title, vec(screen_rect.width/2 + _panel_margin.x/2 - wave_title.get_width()/2, 60))
        #p2 panel
        screen.blit(p2_surface, (screen_rect.width - _panel_margin.x - p2_surface.get_width() - _player_panels_margin.x, screen_rect.height/3))
        #p1 panel
        screen.blit(p1_surface, (screen_rect.width - _panel_margin.x - p2_surface.get_width() - p1_surface.get_width() - _player_panels_margin.x*2, screen_rect.height/3))
        #labels panel
        screen.blit(labels_surface, (_panel_margin.x + _player_panels_margin.x, screen_rect.height/3 + p1_icon.get_height()))


        
       
            
       
            