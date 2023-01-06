import os, pygame
from enum import Enum
from pygame.math import Vector2 as vec

from domain.utils import colors, enums


ENVIRONMENT = enums.Environment.DEV
__SRC_DOMAIN = "src\\domain\\" if ENVIRONMENT == enums.Environment.DEV else ""

#region Paths
ROOT_PATH = f'{os.getcwd()}\\'
SAVE_PATH = f'{ROOT_PATH}src\\saves\\' if ENVIRONMENT == enums.Environment.DEV else f'{ROOT_PATH}saves\\'

#images
IMAGES_PATH = f"{__SRC_DOMAIN}resources\\images\\"

#fonts
FONTS_PATH = f"{ROOT_PATH}{__SRC_DOMAIN}resources\\fonts\\"

#sounds
SOUNDS_PATH = f"{__SRC_DOMAIN}resources\\sounds\\"
#endregion


#region Names
class Songs(Enum):
    MENU = "menu_caves_of_dawn.mp3"
    WAVE_1 = "wave1_mysterious_celesta.mp3"
#endregion

#region fonts
def px_font(size: int):
    return pygame.font.Font(f'{FONTS_PATH}runescape_uf.ttf', size)
# endregion

#region Anim Path
def get_character_path(charac_name: enums.Characters, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}.png'
    
    return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}\\'

def get_enemy_path(enemy: enums.Enemies, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}enemies\\{str(enemy.value)}\\{str(action.value)}.png'

    return f'{IMAGES_PATH}enemies\\{str(enemy.value)}\\{str(action.value)}\\'

def get_weapon_path(weapon_name: enums.Weapons, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE or action == enums.AnimActions.ICON:
        return f'{IMAGES_PATH}weapons\\{str(weapon_name.value)}\\{str(action.value)}.png'
    
    return f'{IMAGES_PATH}weapons\\{str(weapon_name.value)}\\{str(action.value)}\\'

def get_bullet_path(bullet_type: enums.BulletType):
    path = f'{IMAGES_PATH}weapons\\bullets\\{str(bullet_type.value)}\\'
    if not os.path.exists(path):
        return None
    
    if len(os.listdir(path)) > 1:
        return path
    else:
        return f'{path}01.png'
#endregion

#region Sounds
def get_song(song_name: Songs):
    return f'{SOUNDS_PATH}bg_music\\{str(song_name.value)}'

def get_player_sfx(character: enums.Characters, action: enums.AnimActions):
    path = f'{SOUNDS_PATH}sound_effects\\players\\{str(character.value)}\\{str(action.value)}\\'
    if not os.path.exists(path):
        return None
    
    if len(os.listdir(path)) > 1:
        return path
    else:
        return f'{path}01.mp3'
    
def get_enemy_sfx(enemy: enums.Enemies, action: enums.AnimActions):
    path = f'{SOUNDS_PATH}sound_effects\\enemies\\{str(enemy.value)}\\{str(action.value)}\\'
    if not os.path.exists(path):
        return None
    
    if len(os.listdir(path)) > 1:
        return path
    else:
        return f'{path}01.mp3'
    
def get_weapon_sfx(weapon: enums.Weapons, action: enums.AnimActions):
    path = f'{SOUNDS_PATH}sound_effects\\weapons\\{str(weapon.value)}\\{str(action.value)}\\'
    
    filename = '01'
    match action:
        case enums.AnimActions.RELOAD:
            return f'{path}start.mp3'
        case enums.AnimActions.RELOAD_END:
            return f'{path.replace("_end","")}end.mp3'
        
    if not os.path.exists(path):
        return None
    
    
    if len(os.listdir(path)) > 1:
        return path
    else:
        return f'{path}{filename}.mp3'

def get_ui_sfx(ui_sfx: enums.SFXUI):
    return f'{SOUNDS_PATH}sound_effects\\ui\\{str(ui_sfx.value)}'
#endregion
