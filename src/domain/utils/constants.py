import os, pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, enums
from domain.services import resources


pygame.font.init()
    
POPUPS = {
    "error": {
        "timeout_ms": 1500,
        "fade_in_ms": 300,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "background_color": colors.set_alpha(colors.BLACK, 180),
        "padding": vec(20,10),
        "font": resources.px_font(30)
    },
    "damage":{
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "float_anim_distance": 20,
        "font": resources.px_font(20)
    },
    "health":{
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.GREEN,
        "float_anim_distance": 20,
        "font": resources.px_font(20)
    },
    "blink":{
        "use_blink_anim": True,
        "fade_in_ms": 300,
        "fade_out_ms": 300,
        "text_color": colors.RED,
        "font": resources.px_font(20)
    },
    "wave_title": {
        "timeout_ms": 2500,
        "fade_in_ms": 300,
        "fade_out_ms": 1000,
        "text_color": colors.RED,
        "background_color": colors.set_alpha(colors.BLACK, 180),
        "padding": vec(500,10),
        "font": resources.px_font(80)
    },
    "game_over": {
        "fade_in_ms": 1500,
        "text_color": colors.RED,
        "font": resources.px_font(80)
    }
}

ATTRIBUTE_BARS = {
    "weapon": {
        "bars_count": 13,
        "bar_fill_color": colors.LIGHT_BLUE
    }
}

WAVES = {
    1: {
        "wave_number": 1,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 7,
        "wave_step": 3,
        "wave_interval_s": 60,
        "enemies":[
            {
                "type": enums.Enemies.Z_RUI,
                "count": 1,
                "movement_speed": 0.08,
                "health": 500,
                "damage": 40
            },
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 30,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 30,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 30,
                "movement_speed": 1,
                "health": 18,
                "damage": 24
            }
            
        ]
    },
}

{

    1: {
        "wave_number": 1,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 5,
        "wave_step": 3,
        "wave_interval_s": 60,
        "enemies":[
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 10,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            }
        ]
    },
    2: {
        "wave_number": 2,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 6,
        "wave_step": 4,
        "wave_interval_s": 30,
        "enemies":[
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 11,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            }
        ]
    },
    3: {
        "wave_number": 3,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 6,
        "wave_step": 4,
        "wave_interval_s": 30,
        "enemies":[
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 12,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 5,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20
            }
        ]
    },
    4: {
        "wave_number": 4,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 7,
        "wave_step": 3,
        "wave_interval_s": 30,
        "enemies":[
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 13,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 7,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20
            }
        ]
    },
    5: {
        "wave_number": 5,
        "wave_type": enums.WaveType.SIMPLE,
        "max_alive_enemies": 7,
        "wave_step": 3,
        "wave_interval_s": 30,
        "enemies":[
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 13,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 8,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 3,
                "movement_speed": 1,
                "health": 18,
                "damage": 24
            }
        ]
    }
    #1,18,24
}