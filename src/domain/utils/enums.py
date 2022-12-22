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
    
class Command(Enum):
    RESTART_GAME = 1
    
    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value