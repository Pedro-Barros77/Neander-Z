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
    
class Environment(Enum):
    DEV = 1
    RELEASE = 2
    
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
    SV98 = 'snipers\\sv98'
    
class AnimActions(Enum):
    #players/enemies
    TURN = "turn"
    JUMP = "jump"
    RUN = "run"
    FALL_GROUND = "fall_ground"
    DEATH = "death"
    ATTACK = "attack"
    
    #weapons
    RELOAD = "reload"
    RELOAD_END = "reload_end"
    PUMP = "pump"
    SHOOT = "shoot"
    HIT = "hit"
    EMPTY_TRIGGER = "empty"

    #others
    IDLE = "idle"
    ICON = "icon"
    
class Command(Enum):
    RESTART_GAME = 1
    
    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value



class SFXType(Enum):
    UI = "ui"
    WEAPONS = "weapons"
    PLAYERS = "players"
    ENEMIES = "enemies"

class SFXUI(Enum):
    BTN_CLICK = "btn_click.mp3"
    BTN_HOVER = "btn_hover.mp3"
    STORE_PURCHASE = "purchase.mp3"
    
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
    






