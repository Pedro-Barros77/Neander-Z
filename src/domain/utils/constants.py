import os, pygame
from pygame.math import Vector2 as vec

from domain.utils import enums
from domain.utils import colors

DEV_ENV = True

SRC_DOMAIN = "src\\domain\\"


if not DEV_ENV:
    SRC_DOMAIN = ""


ROOT_PATH = f'{os.getcwd()}\\'

IMAGES_PATH = f"{SRC_DOMAIN}resources\\images\\"


FONTS_PATH = f"{ROOT_PATH}{SRC_DOMAIN}resources\\fonts\\"
PIXEL_FONT = f'{FONTS_PATH}runescape_uf.ttf'
SOUNDS_PATH = f"{SRC_DOMAIN}resources\\sounds\\"
MENU_MUSIC = f"{SOUNDS_PATH}bg_music\\menu_caves_of_dawn.mp3"
WAVE_1 = f"{SOUNDS_PATH}bg_music\\wave1_mysterious_celesta.mp3"

if DEV_ENV:
    SAVE_PATH = f'{ROOT_PATH}src\\saves\\'
else:
    SAVE_PATH = f'{ROOT_PATH}saves\\'


GRAVEYARD_MAP = f"{IMAGES_PATH}map_graveyard.png"

ZOMBIE_1 = f"{IMAGES_PATH}enemies\\zombie_1.png"

PISTOL_FOLDER = f"{IMAGES_PATH}weapons\\pistol\\"
SMALL_BULLET = f"{IMAGES_PATH}weapons\\small_bullet\\01.png"

def get_character_frames(charac_name: enums.Characters, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}.png'
    
    return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}\\'

def get_weapon_frames(weapon_name: enums.Weapons, action: enums.AnimActions):
    
    return f'{IMAGES_PATH}weapons\\{str(weapon_name.value)}\\{str(action.value)}\\'

def get_zombie_frames(z_name: enums.Enemies, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}enemies\\{str(z_name.value)}\\{str(action.value)}.png'

    return f'{IMAGES_PATH}enemies\\{str(z_name.value)}\\{str(action.value)}\\'

def get_music(music_name: enums.Music):
    return f'{SOUNDS_PATH}bg_music\\{str(music_name.value)}'

def get_sfx(sfx_type: enums.SFXType, sfx_action: enums.SFXActions, sfx_name: enums.SFXName):
    
    return f'{SOUNDS_PATH}sound_effects\\{str(sfx_type.value)}\\{str(sfx_action.value)}\\{str(sfx_name.value)}'


#     return f'{IMAGES_PATH}enemies\\{str(music_name.value)}\\{str(action.value)}\\'
    

pygame.font.init()
    
POPUPS = {
    "error": {
        "timeout_ms": 1500,
        "fade_in_ms": 300,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "background_color": colors.set_alpha(colors.BLACK, 180),
        "padding": vec(20,10),
        "font": pygame.font.Font(f'{FONTS_PATH}runescape_uf.ttf', 30)
    },
    "damage":{
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "float_anim_distance": 20,
        "font": pygame.font.Font(f'{FONTS_PATH}runescape_uf.ttf', 20)
    },
    "health":{
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.GREEN,
        "float_anim_distance": 20,
        "font": pygame.font.Font(f'{FONTS_PATH}runescape_uf.ttf', 20)
    },
    "blink":{
        "use_blink_anim": True,
        "fade_in_ms": 300,
        "fade_out_ms": 300,
        "text_color": colors.RED,
        "font": pygame.font.Font(f'{FONTS_PATH}runescape_uf.ttf', 20)
    }
}
