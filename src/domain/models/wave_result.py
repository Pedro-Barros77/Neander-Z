from domain.utils import enums
from domain.models.player import Player

class WaveResult():
    def __init__(self, **kwargs):
        self.player: Player = kwargs.pop("player", None)
        self.wave_number = kwargs.pop("wave_number", 1)
        self.score = kwargs.pop("score",0)
        self.money = kwargs.pop("money",0)
        self.kills_count = kwargs.pop("kills_count",0)
        self.headshot_kills_count = kwargs.pop("headshot_kills_count",0)
        self.wave_interval_s: float = kwargs.pop("wave_interval_ms", 10)