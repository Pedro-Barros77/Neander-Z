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
    Z_ROBERT = "z_robert"
    Z_RONALDO = "z_ronaldo"
    Z_RUI = "z_rui"
    Z_RAVEN = "z_raven"
    Z_RAIMUNDO = "z_raimundo"
    Z_RONALD = "z_ronald"
    
class Weapons(Enum):
    P_1911 = 'pistols\\1911'
    DEAGLE = 'pistols\\deagle'
    P_93R = 'pistols\\93r'
    SHORT_BARREL = 'shotguns\\short_barrel'
    UZI = 'smgs\\uzi'
    MACHETE = 'melee\\machete'
    RPG = 'launchers\\rpg'
    SV98 = 'snipers\\sv98'
    M16 = 'rifles\\m16'
    SCAR = 'rifles\\scar'
    DEBUG = 'debug'
    
class Throwables(Enum):
    FRAG_GRENADE = 'throwables\\frag_grenade'
    
class AnimActions(Enum):
    #players/enemies
    TURN = "turn"
    JUMP = "jump"
    RUN = "run"
    ROLL = "roll"
    FALL_GROUND = "fall_ground"
    DEATH = "death"
    ATTACK = "attack"
    BUMP = "bump"
    TAKE_DAMAGE = "damage"
    DASH = "dash"
    
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
    
class WaveType(Enum):
    SIMPLE = 1,
    MEDIUM = 2,
    HARD = 3,
    NIGHTMARE = 4,
    BOSS = 5
    






