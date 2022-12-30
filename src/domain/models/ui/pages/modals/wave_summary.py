import pygame, datetime
from pygame.math import Vector2 as vec

from domain.models.wave_result import WaveResult
from domain.services import menu_controller, game_controller
from domain.utils import colors, constants
from domain.models.ui.button import Button
from domain.models.ui.pages.modals.modal import Modal
from domain.models.ui.pages.modals.store_section import Store

class WaveSummary(Modal):
    def __init__(self, results: tuple[WaveResult, WaveResult], **kwargs):
        super().__init__(**kwargs)

        self.P1_RESULT = results[0]
        self.P2_RESULT = results[1]
        self.p1_ready = False
        self.p2_ready = False
        self.timed_out = False
        self.tab_index = 0
        self.start_time = kwargs.pop("start_time", datetime.datetime.now())
        
        
        self.store_section = Store(self.P1_RESULT.player, self.panel_margin, on_return = lambda: self.set_tab(0))
        
        btn_dict = {
            "text_font": self.font(30),
            "text_color": colors.BLACK
        }

        _btn_pos = vec(self.panel_margin.x, 500)
        _btn_margin = vec(220, 0)
        
        self.buttons: list[Button] = []
        self.buttons.extend([
            Button(vec(_btn_pos), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Store", on_click = lambda: self.set_tab(1),**btn_dict),
            Button(vec(_btn_pos + _btn_margin), f'{constants.IMAGES_PATH}ui\\btn_small.png', scale = 2, text = "Ready", on_click = self.check_btn_ready,**btn_dict),
        ]) 
        self.buttons.append(
            Button(vec(self.buttons[-1].rect.topright), f'{constants.IMAGES_PATH}ui\\btn_square.png', scale = 2, text = "P2", on_click = lambda: None, on_hover = lambda: None, enabled = False,**btn_dict)
        )
    
    def set_tab(self, i: int):
        self.tab_index = i
        match i:
            case 0:
                self.buttons[0].show()
                self.buttons[1].show()
            case 1:
                self.buttons[0].hide()
                self.buttons[1].hide()
           
    
    def check_btn_ready(self):
        self.p1_ready = not self.p1_ready
        btn = self.buttons[1]
        if self.p1_ready:
            btn.set_image(f'{constants.IMAGES_PATH}ui\\btn_small_green.png')
            btn.text_surface = btn.start_text
            btn.set_text('Cancel')
            btn.default_on_hover()
        else:
            btn.set_image(f'{constants.IMAGES_PATH}ui\\btn_small.png')
            btn.text_surface = btn.start_text
            btn.set_text('Ready')
            btn.default_on_hover()
            

    def font(self, size: int):
        return pygame.font.Font(constants.PIXEL_FONT, size)
    
    def draw_summary(self, screen):
        screen_rect = screen.get_rect()
        
        #distance between head icons and character names
        _icon_margin = vec(10, 0)
        #distance between players panels
        _player_panels_margin = vec(30, 0)
       
        wave_title = menu_controller.get_text_surface(f'Survived Wave {self.P1_RESULT.wave_number}', colors.RED, self.font(80))
        p1_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.P1_RESULT.player_character.value}\\head_icon.png'), 4)
        p1_title = menu_controller.get_text_surface(self.P1_RESULT.player_character.value, colors.WHITE, self.font(60))
        
        if self.P2_RESULT != None:
            p2_icon = game_controller.scale_image(pygame.image.load(f'{constants.IMAGES_PATH}ui\\characters\\{self.P2_RESULT.player_character.value}\\head_icon.png'), 4)
            p2_title = menu_controller.get_text_surface(self.P2_RESULT.player_character.value, colors.WHITE, self.font(60))

        lbl_score = menu_controller.get_text_surface("wave score:", colors.WHITE, self.font(28))
        lbl_money = menu_controller.get_text_surface("earned money:", colors.WHITE, self.font(28))
        lbl_kills = menu_controller.get_text_surface("total kills:", colors.WHITE, self.font(28))
        lbl_headshots = menu_controller.get_text_surface("headshot kills:", colors.WHITE, self.font(28))
        
        p1_score = menu_controller.get_text_surface(str(self.P1_RESULT.score), colors.YELLOW, self.font(22))
        p1_money = menu_controller.get_text_surface(f'$ {self.P1_RESULT.money:.2f}', colors.GREEN, self.font(22))
        p1_kills = menu_controller.get_text_surface(str(self.P1_RESULT.kills_count), colors.RED, self.font(22))
        p1_headshots = menu_controller.get_text_surface(str(self.P1_RESULT.headshot_kills_count), colors.RED, self.font(22))
        
        if self.P2_RESULT != None:
            p2_score = menu_controller.get_text_surface(str(self.P2_RESULT.score), colors.YELLOW, self.font(22))
            p2_money = menu_controller.get_text_surface(f'$ {self.P2_RESULT.money:.2f}', colors.GREEN, self.font(22))
            p2_kills = menu_controller.get_text_surface(str(self.P2_RESULT.kills_count), colors.RED, self.font(22))
            p2_headshots = menu_controller.get_text_surface(str(self.P1_RESULT.headshot_kills_count), colors.RED, self.font(22))

        labels = [lbl_score, lbl_money, lbl_kills, lbl_headshots]
        p1_values = [p1_score, p1_money, p1_kills, p1_headshots]
        if self.P2_RESULT != None:
            p2_values = [p2_score, p2_money, p2_kills, p2_headshots]
        
        p1_surface = pygame.Surface((p1_icon.get_width() + p1_title.get_width() + 10, p1_icon.get_height() + 200), pygame.SRCALPHA)
        p1_surface.fill((0,0,0,0))

        if self.P2_RESULT != None:
            p2_surface = pygame.Surface((p2_icon.get_width() + p2_title.get_width() + 10, p2_icon.get_height() + 200), pygame.SRCALPHA)
            p2_surface.fill((0,0,0,0))
        
        labels_surface = pygame.Surface(vec(screen_rect.width - self.panel_margin.x - _player_panels_margin.x - self.panel_margin.x/2 - (_player_panels_margin.x*2),200), pygame.SRCALPHA)
        labels_surface.fill((0,0,0,0))
        
        p1_surface.blit(p1_icon, (0,0))
        p1_surface.blit(p1_title, (p1_icon.get_width() + _icon_margin.x, 0))
        if self.P2_RESULT != None:
            p2_surface.blit(p2_icon, (0,0))
            p2_surface.blit(p2_title, (p2_icon.get_width() + _icon_margin.x, 0))
        
        
        def draw_line(pos:vec, size:int):
            pygame.draw.line(labels_surface, colors.WHITE, pos, pos + vec(size,0), 1)
        
        lbl_margin = vec(10, 40)
        for i, l in enumerate(labels, start=1):
            _lbl_pos = vec(lbl_margin.x, lbl_margin.y * i)
            labels_surface.blit(l, _lbl_pos)
            draw_line(_lbl_pos + vec(0, l.get_height()), labels_surface.get_width())
            p1_surface.blit(p1_values[i-1], (10, _lbl_pos.y - 30  + p1_icon.get_height()))
            if self.P2_RESULT != None:
                p2_surface.blit(p2_values[i-1], (10, _lbl_pos.y - 30 + p1_icon.get_height()))
                pygame.draw.line(p2_surface, colors.WHITE, (0, p2_icon.get_height()), (0, labels_surface.get_height()+12))
                
            pygame.draw.line(p1_surface, colors.WHITE, (0, p1_icon.get_height()), (0, labels_surface.get_height()+12))

        # self.blit_debug(screen, p1_surface = p1_surface, p2_surface = p2_surface, labels_surface = labels_surface)

        #wave title
        screen.blit(wave_title, vec(screen_rect.width/2 + self.panel_margin.x/2 - wave_title.get_width()/2, 60))
        #p2 panel
        if self.P2_RESULT != None:
            screen.blit(p2_surface, (screen_rect.width - self.panel_margin.x - p2_surface.get_width() - _player_panels_margin.x, screen_rect.height/3))
            #p1 panel
            screen.blit(p1_surface, (screen_rect.width - self.panel_margin.x - p2_surface.get_width() - p1_surface.get_width() - _player_panels_margin.x*2, screen_rect.height/3))
        else:
            screen.blit(p1_surface, (screen_rect.width - self.panel_margin.x - p1_surface.get_width()*2 - _player_panels_margin.x*2, screen_rect.height/3))
            
        
        #labels panel
        screen.blit(labels_surface, (self.panel_margin.x + _player_panels_margin.x, screen_rect.height*0.28 + p1_icon.get_height()))

    def draw(self, screen: pygame.Surface):
        #black panel
        super().draw(screen)
        
        if not self.timed_out:
            _elapsed = datetime.datetime.now() - self.start_time
            _remaining = datetime.timedelta(seconds=self.P1_RESULT.wave_interval_s) - _elapsed
            _color = colors.WHITE if _remaining.seconds > 10 else colors.RED
            timer = menu_controller.get_text_surface(f'{_remaining.seconds}s', _color, self.font(50))
            _ms = _remaining.microseconds/1000 - _remaining.seconds/1000
            if _remaining.seconds > 10 or (_ms > 400):
                screen.blit(timer, self.panel_margin + vec(10,10))
        
        match self.tab_index:
            case 0:
                self.draw_summary(screen)
            case 1:
                self.store_section.draw(screen)
        
        for b in self.buttons:
            if b.text == "P2":
                if self.P2_RESULT == None:
                    continue
                b.rect.left = self.buttons[1].rect.right
                b.rect.centery = self.buttons[1].rect.centery
                if self.p2_ready:
                    b.set_image(f'{constants.IMAGES_PATH}ui\\btn_square_green.png')
                else:
                    b.set_image(f'{constants.IMAGES_PATH}ui\\btn_square.png')
                    
            b.draw(screen)


    def update(self, **kwargs):
        super().update()
        events = kwargs.pop("events", [])
        
        if self.tab_index == 1:
            self.store_section.update(events = events)
        
        for b in self.buttons:
            b.update()
            
        if datetime.datetime.now() > self.start_time + datetime.timedelta(seconds= self.P1_RESULT.wave_interval_s):
            self.timed_out = True
            
    def blit_debug(self, screen, **kwargs):
        pygame.draw.rect(kwargs["p1_surface"], colors.GREEN, kwargs["p1_surface"].get_rect(),3)
        pygame.draw.rect(kwargs["p2_surface"], colors.GREEN, kwargs["p2_surface"].get_rect(),3)
        pygame.draw.rect(kwargs["labels_surface"], colors.GREEN, kwargs["labels_surface"].get_rect(),3)
        
       
            
       
            