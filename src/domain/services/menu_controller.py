import pygame, sys, datetime, time
from pygame import locals as ls
from pygame.math import Vector2 as vec

from domain.services.save_manager import SaveManager
from domain.services import resources
from domain.utils import constants, enums, math_utillity as math, colors
from domain.models.ui.popup_text import Popup

pages_history: list = []
save_manager = SaveManager('.save', resources.SAVE_PATH)
playing = False
player_state = {
    "state_name": "player",
    "character": enums.Characters.CARLOS,
    "movement_speed": 0.49,
    "jump_force": 9,
    "max_health": 100
}
config_state = {
    "state_name": "config",
    "ip": "",
    "port": ""
}

dt = 0


popup_group = pygame.sprite.Group()

def save_states(states: list[object]):
    state_names = [s["state_name"] for s in states]
    save_manager.save_game_data(states, state_names)

def save_all_states():
    global config_state, player_state
    _states = [config_state, player_state]
    save_manager.save_game_data(_states, [s["state_name"] for s in _states])

def load_all_states():
    global config_state, player_state
    _states = [config_state, player_state]
    config_state, player_state = save_manager.load_game_data([s["state_name"] for s in _states], _states)

def popup(popup: Popup, center = False):
    global pages_history
    if popup.unique and len([p.name for p in popup_group.sprites() if p.name == popup.name]) > 0:
        return
    if center:
        popup.rect.center = vec(pages_history[-1].screen.get_size())/2
        popup.start_pos = vec(popup.rect.topleft)
    popup_group.add(popup)

def quit_app():
    """Stops the game and closes application.
    """
    pygame.display.quit()
    pygame.quit()
    sys.exit()
    

def get_text_surface(text: str, color: tuple[int,int,int], font: pygame.font.Font):      
    r, g, b, *a = color
    color = (r,g,b)
            
    text_surface = font.render(text, False, color)
    if len(a) > 0:
        text_surface.set_alpha(a[0])
    return text_surface

def is_current_page(page):
    global pages_history
    return pages_history[-1].name == page.name

def start_page(page):
    global pages_history
    pygame.key.set_repeat(200, 25)
    pages_history.append(page)
    app_loop()

def fade_out_color(color: tuple[int,int,int], start_alpha: int, start_time: datetime.datetime, end_time: datetime.datetime):
        
        now = datetime.datetime.now().timestamp()
        start = start_time.timestamp()
        end = end_time.timestamp()
        
        if start > now:
            return colors.alpha_or_default(color, start_alpha)
        
        percentage = ((now - start) / (end - start)) * 100
        percentage = math.clamp(percentage, 0, 100)
        alpha = (start_alpha*(100-percentage))/100
        alpha = math.clamp(alpha, 0, start_alpha)
        return colors.set_alpha(color, int(alpha))

def fade_in_color(color: tuple[int,int,int], target_alpha: int, start_time: datetime.datetime, end_time: datetime.datetime):
        
        now = datetime.datetime.now().timestamp()
        start = start_time.timestamp()
        end = end_time.timestamp()
        
        if start > now:
            return colors.alpha_or_default(color, 0)
        
        percentage = ((now - start) / (end - start)) * 100
        percentage = math.clamp(percentage, 0, 100)
        alpha = (target_alpha*percentage)/100
        alpha = math.clamp(alpha, 0, target_alpha)
        return colors.set_alpha(color, int(alpha))

def play_music(music_name, volume: float, repeat_count: int = -1 ):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music_name)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(repeat_count)
        
clock = pygame.time.Clock()
def app_loop():
    
    last_frame_time = time.time()
    pygame.event.set_allowed([ls.QUIT, ls.KEYDOWN, ls.KEYUP, ls.MOUSEMOTION, ls.MOUSEBUTTONDOWN, ls.MOUSEBUTTONUP, ls.USEREVENT])
    global clock, pages_history, playing, dt
    while 1:
        dt = (time.time() - last_frame_time) * 60
        last_frame_time = time.time()
        
        current_page = pages_history[-1]

        _events = pygame.event.get()
        for event in _events:
            if event.type == pygame.QUIT:
                quit_app()
            if event.type == pygame.KEYDOWN and current_page.name == "Game":
                if event.key == pygame.K_UP:
                    current_page.player.money += 100
                if event.key == pygame.K_DOWN:
                    current_page.player.money -= 100
                
        
        playing = current_page.name == "Game"
            
        # update
        current_page.update(events = _events)
        popup_group.update()
        
        # draw
        current_page.draw()
        
        for p in popup_group.sprites():
            p.draw(current_page.screen)
            
        _txt_fps = get_text_surface(f'fps: {clock.get_fps():.0f}', colors.LIGHT_GRAY, pygame.font.SysFont('calibri', 20))
        _txt_fps_rect = _txt_fps.get_rect()
        _txt_fps_rect.topright = (current_page.screen.get_width() - 20, 20)
        current_page.screen.blit(_txt_fps, _txt_fps_rect)
            
        pygame.display.update()
        clock.tick(60)