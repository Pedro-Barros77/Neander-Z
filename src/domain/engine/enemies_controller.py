import pygame
from pygame.math import Vector2 as vec

from domain.models.enemy import Enemy
from domain.models.enemies.z_roger import ZRoger
from domain.utils import enums, constants

enemies_count = 0

def get_id():
    global enemies_count
    enemies_count += 1
    return enemies_count

def spawn_enemy(game, enemy: Enemy):
    game.enemies_group.add(enemy)
    
def spawn_random_enemy(game):
    spawn_enemy(game, ZRoger((500,300), enums.Enemies.Z_ROGER, movement_speed = 0.12, id = get_id()))

def create_netdata_enemy(game, data: dict):
    e = None
    match data["enemy_name"]:
        case str(enums.Enemies.Z_ROGER.name):
            e = ZRoger((0,0), enums.Enemies.Z_ROGER)
            e.load_net_data(data)
    
    if e != None:
        spawn_enemy(game, e)