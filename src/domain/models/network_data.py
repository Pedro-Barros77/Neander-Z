import pygame

from domain.utils import colors

class Data:
    def __init__(self, **kwargs):
        self.player_pos = kwargs.pop("player_pos", (0,0))
        self.player_size = kwargs.pop("player_size", (0,0))
        self.player_speed = kwargs.pop("player_speed", (0,0))
        self.player_acceleration = kwargs.pop("player_acceleration", (0,0))
        self.player_last_rect = kwargs.pop("player_last_rect", pygame.Rect(self.player_pos, self.player_size))
        
        self.player2_mouse_pos = kwargs.pop("player2_mouse_pos", (0,0))
        self.player2_offset_camera = kwargs.pop("player2_offset_camera", (0,0))
        self.player2_aim_angle = kwargs.pop("player2_aim_angle", 0)
        
        self.net_id = kwargs.pop("net_id", 0)
        self.command_id = kwargs.pop("command_id", 0)
        self.message = kwargs.pop("message", "")