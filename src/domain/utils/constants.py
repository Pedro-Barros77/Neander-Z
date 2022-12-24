import os, pygame
from pygame.math import Vector2 as vec

from domain.utils import enums
from domain.utils import colors

ROOT_PATH = f'{os.getcwd()}\\'

IMAGES_PATH = "src\\domain\\resources\\images\\"
FONTS_PATH = "src\\domain\\resources\\fonts\\"
PIXEL_FONT = f'{FONTS_PATH}runescape_uf.ttf'

SAVE_PATH = f'{ROOT_PATH}src\\saves\\'

GRAVEYARD_MAP = f"{IMAGES_PATH}map_graveyard.png"

ZOMBIE_1 = f"{IMAGES_PATH}enemies\\zombie_1.png"

PISTOL_FOLDER = f"{IMAGES_PATH}weapons\\pistol\\"
SMALL_BULLET = f"{IMAGES_PATH}weapons\\small_bullet\\01.png"


def get_character_frames(charac_name: enums.Characters, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}.png'
    
    return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}\\'

def get_zombie_frames(z_name: enums.Enemies, action: enums.AnimActions):
    return f'{IMAGES_PATH}enemies\\{str(z_name.value)}\\{str(action.value)}\\'
    

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
    }
}
