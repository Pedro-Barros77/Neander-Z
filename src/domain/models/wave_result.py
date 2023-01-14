from domain.utils import enums
from domain.models.player import Player

class WaveResult():
    def __init__(self, **kwargs):
        self.player: Player = kwargs.pop("player", None)
        self.player_character = kwargs.pop("player_character", enums.Characters.CARLOS)
        self.wave_number = kwargs.pop("wave_number", 1)
        self.score = kwargs.pop("score",0)
        self.money = kwargs.pop("money",0)
        self.kills_count = kwargs.pop("kills_count",0)
        self.headshot_kills_count = kwargs.pop("headshot_kills_count",0)
        self.bullets_shot = kwargs.pop("bullets_shot", 0)
        self.bullets_hit = kwargs.pop("bullets_hit", 0)
        
        self.wave_interval_s: float = kwargs.pop("wave_interval_ms", 10)
        
    def get_netdata(self):
        values = {
            "player_character": self.player_character.name,
            "wave_number": self.wave_number,
            "score": self.score,
            "money": self.money,
            "kills_count": self.kills_count,
            "headshot_kills_count": self.headshot_kills_count,
            "wave_interval_s": self.wave_interval_s
        }
        return values
    
    def load_netdata(self, data: dict):
        self.player_character = enums.Characters[data.pop("player_character", str(enums.Characters.CARLOS.name))]
        
        for item, value in data.items():
            setattr(self, item, value)
            
        return self