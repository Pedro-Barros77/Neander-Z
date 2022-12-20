from enum import Enum
from domain.utils import enums
import os

ROOT_PATH = f'{os.getcwd()}\\'

IMAGES_PATH = "src\\domain\\resources\\images\\"
FONTS_PATH = "src\\domain\\resources\\fonts\\"

SAVE_PATH = f'{ROOT_PATH}src\\saves\\'

GRAVEYARD_MAP = f"{IMAGES_PATH}map_graveyard.png"

ZOMBIE_1 = f"{IMAGES_PATH}enemies\\zombie_1.png"

PISTOL_FOLDER = f"{IMAGES_PATH}weapons\\pistol\\"
SMALL_BULLET = f"{IMAGES_PATH}weapons\\small_bullet\\01.png"


def get_character_frames(charac_name: enums.Characters, action: enums.AnimActions):
    if action == enums.AnimActions.IDLE:
        return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}.png'
    
    return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}\\'

def get_zombie_frames(z_name: enums.Characters, action: enums.AnimActions):
    return f'{IMAGES_PATH}enemies\\{str(z_name.value)}\\{str(action.value)}\\'
    
