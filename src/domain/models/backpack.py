
from domain.utils import enums


class BackPack:
    def __init__(self):
        self.max_pistol_ammo = 50
        self.max_shotgun_ammo = 20
        self.max_rifle_ammo = 90
        self.max_sniper_ammo = 15
        self.max_rocket_ammo = 5
        
        self.pistol_ammo = 30
        self.shotgun_ammo = 30
        self.rifle_ammo = 0
        self.sniper_ammo = 0
        self.rocket_ammo = 0
        
        
        
    def set_ammo(self, value: int, ammo_type: enums.BulletType):
        match ammo_type:
            case enums.BulletType.PISTOL:
                self.pistol_ammo = value
                
            case enums.BulletType.SHOTGUN:
                self.shotgun_ammo = value
                
            case enums.BulletType.ASSAULT_RIFLE:
                self.rifle_ammo = value

            case enums.BulletType.SNIPER:
                self.sniper_ammo = value

            case enums.BulletType.ROCKET:
                self.rocket_ammo = value
                
                
                
    def get_ammo(self, ammo_type: enums.BulletType):
        match ammo_type:
            case enums.BulletType.PISTOL:
                return self.pistol_ammo
                
            case enums.BulletType.SHOTGUN:
                return self.shotgun_ammo
                
            case enums.BulletType.ASSAULT_RIFLE:
                return self.rifle_ammo

            case enums.BulletType.SNIPER:
                return self.sniper_ammo

            case enums.BulletType.ROCKET:
                return self.rocket_ammo
            
            
    def set_max_ammo(self, value: int, ammo_type: enums.BulletType):
        match ammo_type:
            case enums.BulletType.PISTOL:
                self.max_pistol_ammo = value
                
            case enums.BulletType.SHOTGUN:
                self.max_shotgun_ammo = value
                
            case enums.BulletType.ASSAULT_RIFLE:
                self.max_rifle_ammo = value

            case enums.BulletType.SNIPER:
                self.max_sniper_ammo = value

            case enums.BulletType.ROCKET:
                self.max_rocket_ammo = value     
    
    def get_max_ammo(self, ammo_type: enums.BulletType):
        match ammo_type:
            case enums.BulletType.PISTOL:
                return self.max_pistol_ammo
                
            case enums.BulletType.SHOTGUN:
                return self.max_shotgun_ammo
                
            case enums.BulletType.ASSAULT_RIFLE:
                return self.max_rifle_ammo

            case enums.BulletType.SNIPER:
                return self.max_sniper_ammo

            case enums.BulletType.ROCKET:
                return self.max_rocket_ammo
            
            
    def can_carry_ammo(self, value:int, ammo_type: enums.BulletType):
        return self.get_ammo(ammo_type) + value <= self.get_max_ammo(ammo_type)