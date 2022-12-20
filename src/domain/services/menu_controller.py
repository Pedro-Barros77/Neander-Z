import pygame, sys, pygame_textinput

from domain.models.ui.pages.page import Page
from domain.services.save_manager import SaveManager
from domain.utils import constants, enums

pages_history: list[Page] = []
save_manager = SaveManager('.save', constants.SAVE_PATH)

player_state = {
    "state_name": "player",
    "character": enums.Characters.CARLOS,
    "movement_speed": 0.5,
    "jump_force": 12,
    "max_health": 100
}
config_state = {
    "state_name": "config",
    "ip": "",
    "port": ""
}

def save_states(states: list[object]):
    state_names = [s["state_name"] for s in states]
    print(state_names)
    save_manager.save_game_data(states, state_names)

def save_all_states():
    global config_state, player_state
    _states = [config_state, player_state]
    save_manager.save_game_data(_states, [s["state_name"] for s in _states])

def load_all_states():
    global config_state, player_state
    _states = [config_state, player_state]
    config_state, player_state = save_manager.load_game_data([s["state_name"] for s in _states], _states)

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

cmd_keys = [pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_KP_ENTER]
def validate_input(txt: pygame_textinput.TextInputVisualizer, key):

    if txt.size != (0,0) and txt.get_line_width(txt.manager.y_cursor) + txt.padding[0] + txt.border_width > txt.size[0] and key not in cmd_keys:
        return False
    
    if (key == pygame.K_KP_ENTER or key == pygame.K_RETURN) and txt.surface.get_height() + txt.font_object.get_height() > txt.size[1] - (txt.border_width*2):
        return False
    
    return True

def start_page(page: Page):
    pygame.key.set_repeat(200, 25)
    pages_history.append(page)
    app_loop()

def app_loop():
    clock = pygame.time.Clock()
    while True:
        _events = pygame.event.get()
        for event in _events:
            if event.type == pygame.QUIT:
                quit_app()
                
        current_page = pages_history[-1]
                
        # update
        current_page.update(events = _events)
        # draw
        current_page.draw()
        
        pygame.display.update()
        clock.tick(60)