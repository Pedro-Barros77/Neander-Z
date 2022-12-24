from domain.utils import enums

class WaveResult():
    def __init__(self, **kwargs):
        self.player_character = kwargs.pop("player_character", enums.Characters.CARLOS)
        self.wave_number = kwargs.pop("wave_number", 1)
        self.score = kwargs.pop("score",0)
        self.money = kwargs.pop("money",0)
        self.kills_count = kwargs.pop("kills_count",0)