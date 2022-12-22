import pygame
from pygame.math import Vector2 as vec

from domain.models.enemy import Enemy
from domain.models.enemies.z_roger import ZRoger
from domain.utils import enums
from domain.models.weapons.small_bullet import SmallBullet
from domain.services import game_controller

def spawn_enemy(game, enemy: Enemy):
    game.enemies_group.add(enemy)
    
def spawn_random_enemy(game):
    spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = game_controller.get_enemy_id()))

def create_netdata_enemy(game, data: dict):
    e = None
    match data["enemy_name"]:
        case str(enums.Enemies.Z_ROGER.name):
            e = ZRoger((0,0), enums.Enemies.Z_ROGER)
            e.load_netdata(data)
    
    if e != None:
        spawn_enemy(game, e)
        
def create_netdata_bullet(game, data: dict):
    b = None
    match data["bullet_name"]:
        case str(enums.Bullets.SMALL_BULLET.name):
            b = SmallBullet(vec(0,0), 0, 0, 0, '', 0)
            b.load_netdata(data)
    
    if b != None:
        game.bullets_group.add(b)