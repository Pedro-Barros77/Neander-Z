from enum import Enum
import os

SERVER_ADDRESS = '000.000.00.000'
SERVER_PORT = 0000

ROOT_PATH = f'{os.getcwd()}\\'

IMAGES_PATH = "src\\domain\\resources\\images\\"

PLAYER_1_IMAGE = f"{IMAGES_PATH}characters\\carlos\\idle.png"
PLAYER_2_IMAGE = f"{IMAGES_PATH}cleiton.png"

GRAVEYARD_MAP = f"{IMAGES_PATH}map_graveyard.png"

ZOMBIE_1 = f"{IMAGES_PATH}enemies\\zombie_1.png"

PISTOL_FOLDER = f"{IMAGES_PATH}weapons\\pistol\\"

class Characters(Enum):
    CARLOS = "carlos"
    CLEITON = "cleiton"

class Actions(Enum):
    TURN = "turn"
    JUMP = "jump"
    RUN = "run"
    FALL_GROUND = "fall_ground"

def get_character_frames(charac_name: str, action: Actions):
    return f'{IMAGES_PATH}characters\\{str(charac_name.value)}\\{str(action.value)}\\'
    
