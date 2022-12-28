from enum import Enum

class ClientType(Enum):
    UNDEFINED = 0
    HOST = 1
    GUEST = 2
    SINGLE = 3
    
    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value
    
    
class Orientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    
class Characters(Enum):
    CARLOS = "carlos"
    CLEITON = "cleiton"
    
class Enemies(Enum):
    Z_ROGER = "z_roger"

class Bullets(Enum):
    SMALL_BULLET = "small_bullet"
    
class AnimActions(Enum):
    TURN = "turn"
    JUMP = "jump"
    RUN = "run"
    FALL_GROUND = "fall_ground"
    IDLE = "idle"
    ATTACK = "attack"
    DEATH = "death"
    
class Command(Enum):
    RESTART_GAME = 1
    
    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value

class Music(Enum):
    MUSIC_MENU = "menu_caves_of_dawn.mp3"
    WAVE_1 = "wave1_mysterious_celesta.mp3"

class SFXType(Enum):
    UI = "ui"
    WEAPONS = "weapons"
    SFX_PLAYER = "sfx_player"

class SFXActions(Enum):
    SHOOT = "shoot"
    RELOAD = "reload"
    CLICKED = "clicked"
    JUMP = "jump"
    HOVER = "hover"
    EMPTY_M = "empty"

class SFXName(Enum):
    P_1911 = "1911.mp3"
    RELOAD_1911 = "reload_1911.mp3"
    EMPTY_1911 = "empty_1911.mp3"
    BTN_CLICK = "btn_click.mp3"
    BTN_HOVER = "btn_hover.mp3"
    






