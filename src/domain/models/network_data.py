class Data:
    def __init__(self, **kwargs):
        self.player_rect = kwargs.pop("player_rect", (0,0, 1,1))
        self.player_speed = kwargs.pop("player_speed", (0,0))
        self.player_acceleration = kwargs.pop("player_acceleration", (0,0))
        self.player_last_rect = kwargs.pop("player_last_rect", self.player_rect)
        self.player_health = kwargs.pop("player_health", 0)
        
        #animation
        self.player_turning_dir = kwargs.pop("player_turning_dir", 0)
        self.player_jumping = kwargs.pop("player_jumping", False)
        self.player_running = kwargs.pop("player_running", False)
        self.player_falling_ground = kwargs.pop("player_falling_ground", False)
        self.player_firing = kwargs.pop("player_firing", False)
        
        self.player_mouse_pos = kwargs.pop("player_mouse_pos", (0,0))
        self.player_aim_angle = kwargs.pop("player_aim_angle", 0)
        
        self.net_id = kwargs.pop("net_id", 0)
        self.command_id = kwargs.pop("command_id", 0)
        
        self.enemies = []
        self.bullets = []
        
        self._json_size_ = ""