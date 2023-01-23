import os
import pygame
from pygame.math import Vector2 as vec

from domain.utils import colors, enums
from domain.services import resources

from domain.content.weapons.semi_auto import SemiAuto
from domain.content.weapons.shotgun import Shotgun
from domain.content.weapons.full_auto import FullAuto
from domain.content.weapons.melee import Melee
from domain.content.weapons.launcher import Launcher
from domain.content.weapons.sniper import Sniper
from domain.content.weapons.burst_fire import BurstFire
from domain.models.weapon import Weapon


pygame.font.init()

HOLD_TRIGGER_FIREMODES = [enums.FireMode.FULL_AUTO, enums.FireMode.MELEE]


def get_weapon(weapon: enums.Weapons, pos: vec, **kwargs):
    w: Weapon = None
    match weapon:
        case enums.Weapons.DEBUG:
            w = FullAuto(pos,
                         bullet_type=enums.BulletType.ASSAULT_RIFLE,
                         weapon_type=enums.Weapons.SCAR,
                         is_primary=False,
                         fire_mode=enums.FireMode.FULL_AUTO,
                         reload_type=enums.ReloadType.MAGAZINE,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="DEV'S weapon",
                         weapon_switch_ms=5,
                         damage=9999,
                         bullet_speed=30,
                         fire_rate=7,
                         reload_delay_ms=50,
                         magazine_size=99999,
                         bullet_max_range=2000,
                         bullet_min_range=1900,
                         reload_end_frame=9,
                         reload_speed_multiplier=4,
                         barrel_offset=vec(0, 7),
                         weapon_scale=1,
                         store_scale=1.8
                         )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 20, 0)
            for s in w.shoot_sounds:
                s.set_volume(0.3)

            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.3)

        case enums.Weapons.MACHETE:
            w = Melee(pos,
                      bullet_type=enums.BulletType.MELEE,
                      weapon_type=weapon,
                      is_primary=False,
                      fire_mode=enums.FireMode.MELEE,
                      reload_type=enums.ReloadType.NO_RELOAD,
                      upgrades_dict=get_weapon_upgrade(weapon),
                      display_name="Machete",
                      weapon_switch_ms=150,
                      damage=3,
                      bullet_speed=0,
                      fire_rate=2,
                      reload_delay_ms=0,
                      magazine_size=0,
                      bullet_max_range=1,
                      bullet_min_range=1,
                      reload_end_frame=0,
                      barrel_offset=vec(0, 0),
                      hit_frame=8,
                      attack_box=vec(50, 20),
                      weapon_scale=0.08,
                      store_scale=0.2,
                      stamina_use=2
                      )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 30, 0)
            for s in w.swipe_sounds:
                s.set_volume(0.5)

            for h in w.hit_sounds:
                h.set_volume(0.5)

        case enums.Weapons.P_1911:
            w = SemiAuto(pos,
                         bullet_type=enums.BulletType.PISTOL,
                         weapon_type=weapon,
                         is_primary=False,
                         fire_mode=enums.FireMode.SEMI_AUTO,
                         reload_type=enums.ReloadType.MAGAZINE,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="Colt 1911",
                         weapon_switch_ms=200,
                         damage=6,
                         bullet_speed=30,
                         fire_rate=4,
                         reload_delay_ms=1000,
                         magazine_size=7,
                         bullet_max_range=600,
                         bullet_min_range=400,
                         reload_end_frame=6,
                         reload_speed_multiplier=2,
                         barrel_offset=vec(0, 7),
                         store_scale=1,
                         )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 20, 0)
            for s in w.shoot_sounds:
                s.set_volume(0.1)

      
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.5)
        
        case enums.Weapons.DEAGLE:
            w = SemiAuto(pos,
                         bullet_type=enums.BulletType.ASSAULT_RIFLE,
                         weapon_type=weapon,
                         is_primary=False,
                         fire_mode=enums.FireMode.SEMI_AUTO,
                         reload_type=enums.ReloadType.MAGAZINE,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="Desert Eagle",
                         weapon_switch_ms=200,
                         damage=10,
                         bullet_speed=30,
                         fire_rate=3,
                         reload_delay_ms=1100,
                         magazine_size=7,
                         weapon_scale= 0.8,
                         bullet_max_range=700,
                         bullet_min_range=600,
                         reload_end_frame=12,
                         reload_speed_multiplier=2,
                         barrel_offset=vec(0, 15),
                         store_scale=1,
                         )
            w.bullet_spawn_offset = vec(w.rect.width/2 , -5)
            for s in w.shoot_sounds:
                s.set_volume(0.3)
         
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.5)

        case enums.Weapons.SHORT_BARREL:
            w = Shotgun(pos,
                        bullet_type=enums.BulletType.SHOTGUN,
                        weapon_type=weapon,
                        is_primary=True,
                        fire_mode=enums.FireMode.PUMP_ACTION,
                        reload_type=enums.ReloadType.SINGLE_BULLET,
                        upgrades_dict=get_weapon_upgrade(weapon),
                        display_name="Short Barrel",
                        weapon_switch_ms=350,
                        damage=3,
                        bullet_speed=20,
                        fire_rate=1.5,
                        reload_delay_ms=500,
                        magazine_size=5,
                        dispersion=50,
                        ballin_count=12,
                        weapon_scale=1.5,
                        bullet_max_range=300,
                        bullet_min_range=200,
                        reload_end_frame=8,
                        reload_speed_multiplier=2,
                        barrel_offset=vec(0, 7),
                        store_scale=1.8
                        )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 25, 5)
            w.shoot_sound.set_volume(0.5)
            w.pump_sound.set_volume(0.5)
            w.empty_sound.set_volume(0.1)
            w.reload_end_sound.set_volume(0.5)

        case enums.Weapons.UZI:
            w = FullAuto(pos,
                         bullet_type=enums.BulletType.PISTOL,
                         weapon_type=weapon,
                         is_primary=True,
                         fire_mode=enums.FireMode.FULL_AUTO,
                         reload_type=enums.ReloadType.MAGAZINE,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="UZI",
                         weapon_switch_ms=220,
                         damage=4,
                         bullet_speed=20,
                         fire_rate=10,
                         reload_delay_ms=1200,
                         magazine_size=25,
                         bullet_max_range=500,
                         bullet_min_range=300,
                         reload_end_frame=10,
                         reload_speed_multiplier=4,
                         barrel_offset=vec(0, 7),
                         weapon_scale=1.2,
                         store_scale=1.1
                         )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 40, 2)
            for s in w.shoot_sounds:
                s.set_volume(0.5)

            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.3)

        case enums.Weapons.RPG:
            w = Launcher(pos,
                         bullet_type=enums.BulletType.ROCKET,
                         weapon_type=weapon,
                         is_primary=True,
                         fire_mode=enums.FireMode.SINGLE_SHOT,
                         reload_type=enums.ReloadType.SINGLE_BULLET,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="RPG",
                         weapon_switch_ms=500,
                         damage=50,
                         bullet_speed=15,
                         fire_rate=1,
                         reload_delay_ms=3000,
                         magazine_size=1,
                         bullet_max_range=800,
                         bullet_min_range=790,
                         explosion_min_radius=100,
                         explosion_max_radius=200,
                         reload_start_frame=12,
                         reload_end_frame=17,
                         reload_speed_multiplier=2,
                         barrel_offset=vec(-15, 3),
                         store_scale=2.2
                         )
            w.bullet_spawn_offset = vec(
                w.rect.width/2, -10) + vec(w.barrel_offset)
            w.shoot_sound.set_volume(0.1)
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound_launcher.set_volume(0.3)
            w.reload_end_sound.set_volume(0.5)

        case enums.Weapons.SV98:
            w = Sniper(pos,
                       bullet_type=enums.BulletType.SNIPER,
                       weapon_type=weapon,
                       is_primary=True,
                       fire_mode=enums.FireMode.BOLT_ACTION,
                       reload_type=enums.ReloadType.MAGAZINE,
                       upgrades_dict=get_weapon_upgrade(weapon),
                       display_name="SV98",
                       weapon_switch_ms=400,
                       damage=25,
                       bullet_speed=35,
                       fire_rate=1,
                       reload_delay_ms=1500,
                       magazine_size=5,
                       bullet_max_range=1200,
                       bullet_min_range=1000,
                       reload_end_frame=17,
                       reload_speed_multiplier=9,
                       barrel_offset=vec(10, -5),
                       pierce_damage_multiplier=0.5,
                       max_pierce_targets=5,
                       weapon_scale=1.1,
                       store_scale=2.3
                       )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 20, -3)
            w.shoot_sound.set_volume(0.5)
            w.pump_sound.set_volume(0.5)
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.3)

        case enums.Weapons.M16:
            w = BurstFire(pos,
                          bullet_type=enums.BulletType.ASSAULT_RIFLE,
                          weapon_type=weapon,
                          is_primary=True,
                          fire_mode=enums.FireMode.BURST,
                          reload_type=enums.ReloadType.MAGAZINE,
                          upgrades_dict=get_weapon_upgrade(weapon),
                          display_name="M16",
                          weapon_switch_ms=350,
                          damage=10,
                          bullet_speed=35,
                          fire_rate=4,
                          burst_fire_rate=12,
                          burst_count=3,
                          reload_delay_ms=2500,
                          magazine_size=20,
                          bullet_max_range=800,
                          bullet_min_range=600,
                          reload_start_frame=5,
                          reload_end_frame=10,
                          reload_speed_multiplier=12,
                          barrel_offset=vec(0, 3),
                          weapon_scale=1.3,
                          store_scale=2
                          )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 5, 0)
            for s in w.shoot_sounds:
                s.set_volume(0.3)
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound_burst.set_volume(0.3)
            w.reload_end_sound.set_volume(0.4)

        case enums.Weapons.P_93R:
            w = BurstFire(pos,
                          bullet_type=enums.BulletType.PISTOL,
                          weapon_type=weapon,
                          is_primary=False,
                          fire_mode=enums.FireMode.BURST,
                          reload_type=enums.ReloadType.MAGAZINE,
                          upgrades_dict=get_weapon_upgrade(weapon),
                          display_name="Beretta 93R",
                          weapon_switch_ms=230,
                          damage=4,
                          bullet_speed=30,
                          fire_rate=5,
                          burst_fire_rate=12,
                          burst_count=3,
                          reload_delay_ms=1500,
                          magazine_size=15,
                          bullet_max_range=600,
                          bullet_min_range=400,
                          reload_end_frame=12,
                          reload_speed_multiplier=8,
                          barrel_offset=vec(0, 4),
                          weapon_scale=0.5,
                          store_scale=1.1
                          )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 20, -3)
            for s in w.shoot_sounds:
                s.set_volume(0.3)
            w.empty_sound.set_volume(0.1)
            w.reload_start_sound_burst.set_volume(0.3)
            w.reload_end_sound.set_volume(0.4)

        case enums.Weapons.SCAR:
            w = FullAuto(pos,
                         bullet_type=enums.BulletType.ASSAULT_RIFLE,
                         weapon_type=weapon,
                         is_primary=True,
                         fire_mode=enums.FireMode.FULL_AUTO,
                         reload_type=enums.ReloadType.MAGAZINE,
                         upgrades_dict=get_weapon_upgrade(weapon),
                         display_name="SCAR-L",
                         weapon_switch_ms=350,
                         damage=10,
                         bullet_speed=30,
                         fire_rate=7,
                         reload_delay_ms=1200,
                         magazine_size=25,
                         bullet_max_range=750,
                         bullet_min_range=600,
                         reload_end_frame=9,
                         reload_speed_multiplier=4,
                         barrel_offset=vec(0, 7),
                         weapon_scale=1,
                         store_scale=1.8
                         )
            w.bullet_spawn_offset = vec(w.rect.width/2 + 20, 0)
            for s in w.shoot_sounds:
                s.set_volume(0.3)

            w.empty_sound.set_volume(0.1)
            w.reload_start_sound.set_volume(0.3)
            w.reload_end_sound.set_volume(0.3)

    w.weapon_anchor = kwargs.pop("weapon_anchor", vec(0, 0))
    w.weapon_distance = kwargs.pop("weapon_distance", 0)
    w.player_backpack = kwargs.pop("backpack", None)
    w.load_content = kwargs.pop("load_content", True)

    return w


def get_weapon_upgrade(weapon_type: enums.Weapons):
    if weapon_type in WEAPONS_UPGRADES.keys():
        return WEAPONS_UPGRADES[weapon_type]
    else:
        return None
    
def get_player_upgrade(character_name: enums.Characters):
    if character_name in ITEMS_UPGRADES.keys():
        return ITEMS_UPGRADES[character_name]
    else:
        return None


ITEMS_UPGRADES = {
    "backpack": [
        {
            "id": 1,
            "max_pistol_ammo": 10,
            "max_shotgun_ammo": 5,
            "max_rifle_ammo": 10,
            "max_sniper_ammo": 0,
            "max_rocket_ammo": 1,
            "price": 150.00
        },
        {
            "id": 2,
            "max_pistol_ammo": 10,
            "max_shotgun_ammo": 10,
            "max_rifle_ammo": 10,
            "max_sniper_ammo": 5,
            "max_rocket_ammo": 1,
            "price": 350.00
        },
        {
            "id": 3,
            "max_pistol_ammo": 20,
            "max_shotgun_ammo": 10,
            "max_rifle_ammo": 20,
            "max_sniper_ammo": 5,
            "max_rocket_ammo": 1,
            "price": 500.00
        },
        {
            "id": 4,
            "max_pistol_ammo": 20,
            "max_shotgun_ammo": 10,
            "max_rifle_ammo": 20,
            "max_sniper_ammo": 5,
            "max_rocket_ammo": 1,
            "price": 850.00
        },
        {
            "id": 5,
            "max_pistol_ammo": 20,
            "max_shotgun_ammo": 10,
            "max_rifle_ammo": 20,
            "max_sniper_ammo": 5,
            "max_rocket_ammo": 1,
            "price": 1200.00
        },
    ],
    enums.Characters.CARLOS: {
        "max_health": [#half: 15
            {
                "id": 1,
                "ammount": 15,
                "price": 150.00
            },
        ],
        "movement_speed": [#half: 0.29
            {
                "id": 1,
                "ammount": 0.029,
                "price": 150.00
            },
        ],
        "sprint_speed": [#half: 0.054
            {
                "id": 1,
                "ammount": 0.054,
                "price": 150.00
            },
        ],
        "jump_force": [#half: 0.46
            {
                "id": 1,
                "ammount": 0.46,
                "price": 150.00
            },
        ],
        "max_stamina": [#half: 62.5
            {
                "id": 1,
                "ammount": 62.5,
                "price": 150.00
            },
        ],
        "stamina_regen_rate": [#half: 0.375
            {
                "id": 1,
                "ammount": 0.375,
                "price": 150.00
            },
        ],
        "stamina_regen_haste": [#half: 0.75
            {
                "id": 1,
                "ammount": 0.75,
                "price": 150.00
            },
        ],
        "jump_stamina_skill": [#half: 2.08
            {
                "id": 1,
                "ammount": 2.08,
                "price": 150.00
            },
        ],
        "sprint_stamina_skill": [#half: 2.5
            {
                "id": 1,
                "ammount": 2.5,
                "price": 150.00
            },
        ],
        "attack_stamina_skill": [#half: 4.17
            {
                "id": 1,
                "ammount": 4.17*5,
                "price": 150.00
            },
        ]
    }
}

WEAPONS_UPGRADES = {
    enums.Weapons.MACHETE: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 3,
                "price": 220.0
            }
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 200.0
            },
        ],
        "stamina": [
            {
                "id": 1,
                "ammount": 0.75,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 0.7,
                "price": 220.0
            },
            {
                "id": 2,
                "ammount": 0.7,
                "price": 220.0
            }
        ],
    },
    enums.Weapons.P_1911: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 210.0
            }
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 70.0
            },
            {
                "id": 2,
                "ammount": 0.5,
                "price": 95.0
            },
            {
                "id": 3,
                "ammount": 1,
                "price": 120.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 30.0
            },
            {
                "id": 2,
                "ammount": 0.5,
                "price": 55.0
            },
            {
                "id": 3,
                "ammount": 0.5,
                "price": 70.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 70.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 100.0
            },
            {
                "id": 3,
                "ammount": 1.3,
                "price": 155.0
            },
            {
                "id": 4,
                "ammount": 1.1,
                "price": 195.0
            }
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 3,
                "price": 95.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 215.0
            },
            {
                "id": 3,
                "ammount": 3,
                "price": 310.0
            }
        ]
    },
    enums.Weapons.DEAGLE: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 210.0
            }
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 70.0
            },
            {
                "id": 2,
                "ammount": 0.5,
                "price": 95.0
            },
            {
                "id": 3,
                "ammount": 1,
                "price": 120.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 30.0
            },
            {
                "id": 2,
                "ammount": 0.5,
                "price": 55.0
            },
            {
                "id": 3,
                "ammount": 0.5,
                "price": 70.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 70.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 100.0
            },
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 1,
                "price": 95.0
            },
            {
                "id": 2,
                "ammount": 1,
                "price": 215.0
            },
            {
                "id": 3,
                "ammount": 3,
                "price": 310.0
            }
        ]
    },
    enums.Weapons.SHORT_BARREL: {
        "damage": [
            {
                "id": 1,
                "ammount": 1,
                "price": 200.0
            },
            {
                "id": 2,
                "ammount": 1,
                "price": 230.0
            },
            {
                "id": 3,
                "ammount": 1,
                "price": 285.0
            }
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 90.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 130.0
            },
            {
                "id": 2,
                "ammount": 0.5,
                "price": 155.0
            },
            {
                "id": 3,
                "ammount": 0.5,
                "price": 270.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 0.8,
                "price": 75.0
            },
            {
                "id": 2,
                "ammount": 1,
                "price": 110.0
            },
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 2,
                "price": 95.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 130.0
            },
        ],
        "concentration": [
            {
                "id": 1,
                "ammount": 1,
                "price": 140.0
            },
            {
                "id": 2,
                "ammount": 1,
                "price": 195.0
            },
            {
                "id": 3,
                "ammount": 1,
                "price": 245.0
            }
        ],
    },
    enums.Weapons.UZI: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 120.0
            },
            {
                "id": 1,
                "ammount": 2,
                "price": 250.0
            },
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.7,
                "price": 90.0
            },
            {
                "id": 2,
                "ammount": 0.7,
                "price": 115.0
            },
            {
                "id": 3,
                "ammount": 0.5,
                "price": 170.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.8,
                "price": 80.0
            },
            {
                "id": 2,
                "ammount": 0.8,
                "price": 115.0
            },
            {
                "id": 3,
                "ammount": 0.8,
                "price": 135.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 1.6,
                "price": 185.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 210.0
            },
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 3,
                "price": 100.0
            },
            {
                "id": 2,
                "ammount": 3,
                "price": 130.0
            },
            {
                "id": 2,
                "ammount": 4,
                "price": 145.0
            },
        ],
    },
    enums.Weapons.RPG: {
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.8,
                "price": 80.0
            },
            {
                "id": 2,
                "ammount": 0.8,
                "price": 115.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 60.0
            },
            {
                "id": 2,
                "ammount": 1.6,
                "price": 75.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 100.0
            },
        ],
    },
    enums.Weapons.SV98: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 2.5,
                "price": 145.0
            },
            {
                "id": 3,
                "ammount": 2.5,
                "price": 180.0
            },
            {
                "id": 4,
                "ammount": 3,
                "price": 220.0
            }
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.7,
                "price": 80.0
            },
            {
                "id": 2,
                "ammount": 0.7,
                "price": 95.0
            },
            {
                "id": 3,
                "ammount": 0.5,
                "price": 120.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.8,
                "price": 125.0
            },
            {
                "id": 2,
                "ammount": 0.8,
                "price": 150.0
            },
            {
                "id": 3,
                "ammount": 0.8,
                "price": 190.0
            }
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 1,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 180.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 235.0
            },
        ],
    },
    enums.Weapons.M16: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 150.0
            },
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.65,
                "price": 100.0
            },
            {
                "id": 2,
                "ammount": 0.9,
                "price": 125.0
            },
            {
                "id": 3,
                "ammount": 1,
                "price": 170.0
            },
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.4,
                "price": 95.0
            },
            {
                "id": 2,
                "ammount": 0.4,
                "price": 120.0
            },
            {
                "id": 3,
                "ammount": 0.4,
                "price": 140.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 1.6,
                "price": 165.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 200.0
            },
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 3,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 3,
                "price": 155.0
            },
            {
                "id": 2,
                "ammount": 4,
                "price": 170.0
            },
        ],
    },
    enums.Weapons.P_93R: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 115.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 135.0
            },
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.5,
                "price": 100.0
            },
            {
                "id": 2,
                "ammount": 1.2,
                "price": 125.0
            }
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.4,
                "price": 110
            },
            {
                "id": 2,
                "ammount": 0.4,
                "price": 125.0
            },
            {
                "id": 3,
                "ammount": 0.4,
                "price": 150.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 1.5,
                "price": 165.0
            },
            {
                "id": 2,
                "ammount": 1,
                "price": 200.0
            },
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 3,
                "price": 120.0
            },
            {
                "id": 2,
                "ammount": 3,
                "price": 155.0
            },
            {
                "id": 2,
                "ammount": 4,
                "price": 170.0
            },
        ],
    },
    enums.Weapons.SCAR: {
        "damage": [
            {
                "id": 1,
                "ammount": 2,
                "price": 180.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 245.0
            },
        ],
        "firerate": [
            {
                "id": 1,
                "ammount": 0.65,
                "price": 100.0
            },
            {
                "id": 2,
                "ammount": 0.9,
                "price": 125.0
            }
        ],
        "reload_speed": [
            {
                "id": 1,
                "ammount": 0.4,
                "price": 150.0
            },
            {
                "id": 2,
                "ammount": 0.4,
                "price": 185.0
            }
        ],
        "range": [
            {
                "id": 1,
                "ammount": 1,
                "price": 125.0
            },
            {
                "id": 2,
                "ammount": 1.4,
                "price": 180.0
            }
        ],
        "magazine_size": [
            {
                "id": 1,
                "ammount": 3,
                "price": 145.0
            },
            {
                "id": 2,
                "ammount": 2,
                "price": 205.0
            },
        ],
    },
}

POPUPS = {
    "error": {
        "timeout_ms": 1500,
        "fade_in_ms": 300,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "background_color": colors.set_alpha(colors.BLACK, 180),
        "padding": vec(20, 10),
        "font": resources.px_font(30)
    },
    "damage": {
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.RED,
        "float_anim_distance": 20,
        "font": resources.px_font(20)
    },
    "health": {
        "timeout_ms": 100,
        "fade_in_ms": 50,
        "fade_out_ms": 500,
        "text_color": colors.GREEN,
        "float_anim_distance": 20,
        "font": resources.px_font(20)
    },
    "blink": {
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
        "padding": vec(500, 10),
        "font": resources.px_font(80)
    },
    "wave_message": {
        "timeout_ms": 2500,
        "fade_in_ms": 300,
        "fade_out_ms": 1000,
        "text_color": colors.YELLOW,
        "background_color": colors.set_alpha(colors.BLACK, 180),
        "padding": vec(500, 10),
        "font": resources.px_font(25)
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
        "bar_fill_color": colors.LIGHT_BLUE,
        "upgrade_blink_ms": 300
    }
}

WAVES = {
    1: {
        "wave_number": 1,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "And so it begins...",
        "timed_spawn_count": 10,
        "spawn_timer_ms": 8000,
        "wave_interval_s": 6000,
        "start_delay_ms": 0,
        "end_delay_ms": 0,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 10,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    }
}

{
    1: {
        "wave_number": 1,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "And so it begins...",
        "timed_spawn_count": 4,
        "spawn_timer_ms": 8000,
        "wave_interval_s": 60,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 10,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    },
    2: {
        "wave_number": 2,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 5,
        "spawn_timer_ms": 8000,
        "wave_interval_s": 60,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 14,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    },
    3: {
        "wave_number": 3,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 6,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 12,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 5,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    },
    4: {
        "wave_number": 4,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "The death comes from above!",
        "timed_spawn_count": 8,
        "spawn_timer_ms": 6500,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 14,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 7,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 5,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    5: {
        "wave_number": 5,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": 'Remember the "Double Tap" rule!',
        "timed_spawn_count": 8,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.6,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 14,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 9,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 6,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 24,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    },
    6: {
        "wave_number": 6,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": 'You hear barks at the distance...',
        "timed_spawn_count": 8,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.6,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 12,
                "movement_speed": 0.12,
                "health": 28,
                "damage": 15,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 10,
                "movement_speed": 0.1,
                "health": 24,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 6,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 24,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 2,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            }
        ]
    },
    7: {
        "wave_number": 7,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": 'Some zombies have evolved...',
        "timed_spawn_count": 9,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.6,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 14,
                "movement_speed": 0.12,
                "health": 32,
                "damage": 16,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 12,
                "movement_speed": 0.1,
                "health": 25,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 6,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 24,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    8: {
        "wave_number": 8,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "I'll take more than a headache to knock em down!",
        "timed_spawn_count": 9,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.6,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 12,
                "movement_speed": 0.12,
                "health": 32,
                "damage": 16,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 11,
                "movement_speed": 0.1,
                "health": 25,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 8,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 24,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 3,
                "movement_speed": 0.09,
                "health": 40,
                "damage": 19,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    9: {
        "wave_number": 9,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 9,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 12,
                "movement_speed": 0.12,
                "health": 32,
                "damage": 16,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 11,
                "movement_speed": 0.1,
                "health": 25,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 8,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 24,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 4,
                "movement_speed": 0.09,
                "health": 40,
                "damage": 19,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 5,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 3,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    10: {
        "wave_number": 10,
        "wave_type": enums.WaveType.BOSS,
        "wave_message": "RUI IS COMMING!",
        "wave_interval_s": 45,
        "timed_spawn_count": 5,
        "spawn_timer_ms": 7000,
        "start_delay_ms": 2000,
        "end_delay_ms": 2500,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_RUI,
                "count": 1,
                "movement_speed": 0.08,
                "health": 750,
                "damage": 40,
                "max_alive": 99,
                "spawn_chance_multiplier": 0
            },
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 1,
                "movement_speed": 0.12,
                "health": 32,
                "damage": 16,
                "max_alive": 99,
                "spawn_chance_multiplier": 3
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 1,
                "movement_speed": 0.1,
                "health": 25,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 4
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 1,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 1,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 2
            },
        ]
    },
    11: {
        "wave_number": 11,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "kill the remnants of the boss fight",
        "timed_spawn_count": 4,
        "spawn_timer_ms": 2000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 40,
                "movement_speed": 0.1,
                "health": 40,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

        ]
    },
    12: {
        "wave_number": 12,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 8,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 15,
                "movement_speed": 0.12,
                "health": 40,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 11,
                "movement_speed": 0.1,
                "health": 28,
                "damage": 22,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 8,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 15,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    13: {
        "wave_number": 13,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 8,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 15,
                "movement_speed": 0.12,
                "health": 40,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 11,
                "movement_speed": 0.1,
                "health": 30,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 8,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 7,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    14: {
        "wave_number": 14,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 8,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 15,
                "movement_speed": 0.12,
                "health": 40,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 11,
                "movement_speed": 0.1,
                "health": 30,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 8,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 4,
                "movement_speed": 0.09,
                "health": 40,
                "damage": 19,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 5,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 10,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    15: {
        "wave_number": 15,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 9,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [

            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 18,
                "movement_speed": 0.1,
                "health": 40,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 12,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 4,
                "movement_speed": 0.09,
                "health": 50,
                "damage": 19,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 5,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

        ]
    },
    16: {
        "wave_number": 16,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "Hope you've saved money so far",
        "timed_spawn_count": 9,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [

            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 5,
                "movement_speed": 0.1,
                "health": 40,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 3,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 18,
                "movement_speed": 0.09,
                "health": 50,
                "damage": 19,
                "max_alive": 99,
                "spawn_chance_multiplier": 3
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 2,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

        ]
    },
    17: {
        "wave_number": 17,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "Look who's back, but more evolved",
        "timed_spawn_count": 9,
        "spawn_timer_ms": 6000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_ROGER,
                "count": 10,
                "movement_speed": 0.15,
                "health": 45,
                "damage": 22,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

            {
                "type": enums.Enemies.Z_RONALDO,
                "count": 18,
                "movement_speed": 0.1,
                "health": 40,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 3,
                "movement_speed": 1,
                "health": 18,
                "damage": 24,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 8,
                "movement_speed": 0.5,
                "health": 1,
                "damage": 5,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },

        ]
    },
    18: {
        "wave_number": 18,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "demon",
        "timed_spawn_count": 15,
        "spawn_timer_ms": 4000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 1,
        "enemies": [

            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 25,
                "movement_speed": 1,
                "health": 18,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 35,
                "movement_speed": 0.5,
                "health": 2,
                "damage": 10,
                "max_alive": 99,
                "spawn_chance_multiplier": 1.7
            },

        ]
    },
    19: {
        "wave_number": 19,
        "wave_type": enums.WaveType.SIMPLE,
        "wave_message": "",
        "timed_spawn_count": 6,
        "spawn_timer_ms": 7000,
        "wave_interval_s": 45,
        "start_delay_ms": 2000,
        "end_delay_ms": 1000,
        "money_multiplier": 0.8,
        "enemies": [
            {
                "type": enums.Enemies.Z_RONALD,
                "count": 15,
                "movement_speed": 0.14,
                "afterlife_chance": 0.45,
                "health": 26,
                "damage": 18,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 18,
                "movement_speed": 0.09,
                "health": 55,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
    20: {
        "wave_number": 20,
        "wave_type": enums.WaveType.BOSS,
        "wave_message": "RUI RETURNED AND BRING HIS TWIN BROTHER WITH HIM!",
        "wave_interval_s": 45,
        "timed_spawn_count": 5,
        "spawn_timer_ms": 7000,
        "start_delay_ms": 2000,
        "end_delay_ms": 2500,
        "money_multiplier": 1,
        "enemies": [
            {
                "type": enums.Enemies.Z_RUI,
                "count": 2,
                "movement_speed": 0.08,
                "health": 750,
                "damage": 40,
                "max_alive": 99,
                "spawn_chance_multiplier": 0
            },
            {
                "type": enums.Enemies.Z_RAIMUNDO,
                "count": 1,
                "movement_speed": 0.09,
                "health": 55,
                "damage": 20,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_ROBERT,
                "count": 1,
                "movement_speed": 1,
                "health": 18,
                "damage": 28,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
            {
                "type": enums.Enemies.Z_RAVEN,
                "count": 1,
                "movement_speed": 0.5,
                "health": 2,
                "damage": 10,
                "max_alive": 99,
                "spawn_chance_multiplier": 1
            },
        ]
    },
}
