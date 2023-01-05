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
    
class Weapons(Enum):
    P_1911 = 'pistols\\1911'
    SHORT_BARREL = 'shotguns\\short_barrel'
    UZI = 'smgs\\uzi'
    MACHETE = 'melee\\machete'
    RPG = 'launchers\\rpg'
    
class AnimActions(Enum):
    TURN = "turn"
    JUMP = "jump"
    RUN = "run"
    RELOAD = "reload"
    PUMP = "pump"
    SHOOT = "shoot"
    FALL_GROUND = "fall_ground"
    IDLE = "idle"
    ATTACK = "attack"
    DEATH = "death"
    ICON = "icon"
    
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
    PUMP = "pump"
    RELOAD = "reload"
    CLICKED = "clicked"
    JUMP = "jump"
    HOVER = "hover"
    EMPTY_M = "empty"

class SFXName(Enum):
    #shoot
    P_1911 = "1911.mp3"
    SHORT_BARREL = "short_barrel.mp3"
    PUMP_SHORT_BARREL = "pump_short_barrel.mp3"
    UZI_SHOOT = "uzi_shoot.mp3"
    MACHETE_SWIPE = "machete_swipe.mp3"
    MACHETE_HIT = "machete_hit.mp3"
    RPG_LAUNCH = "rpg_launch.mp3"
    RPG_EXPLOSION = "rpg_explosion.mp3"
    
    #reload
    START_RELOAD_1911 = "start_reload_1911.mp3"
    END_RELOAD_1911 = "end_reload_1911.mp3"
    SHELL_LOAD_SHORT_BARREL = "shell_load_short_barrel.mp3"
    UZI_RELOAD = "uzi_reload.mp3"
    RPG_START_RELOAD = "rpg_start_reload.mp3"
    RPG_END_RELOAD = "rpg_end_reload.mp3"
    
    #others
    EMPTY_1911 = "empty_1911.mp3"
    BTN_CLICK = "btn_click.mp3"
    BTN_HOVER = "btn_hover.mp3"
    
class BulletType(Enum):
    MELEE = "melee"
    PISTOL = "pistol"
    SHOTGUN = "shotgun"
    ASSAULT_RIFLE = "rifle"
    SNIPER = "sniper"
    ROCKET = "rocket"
    GRENADE = "grenade"
    
class FireMode(Enum):
    MELEE = 0
    SEMI_AUTO = 1
    BURST = 2
    FULL_AUTO = 3
    PUMP_ACTION = 4
    BOLT_ACTION = 5
    SINGLE_SHOT = 6
    
class ReloadType(Enum):
    NO_RELOAD = 0
    MAGAZINE = 1
    SINGLE_BULLET = 2
    
class ConvertType(Enum):
    NO_CONVERT = 0
    CONVERT = 1
    CONVERT_ALPHA = 2
    






