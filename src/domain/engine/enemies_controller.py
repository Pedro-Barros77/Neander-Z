import pygame
from pygame.math import Vector2 as vec

from domain.models.enemy import Enemy
from domain.utils import constants
from domain.models.enemies.zombie_1 import Zombie1
from domain.utils import enums
from domain.services import game_controller


def spawn_enemy(game, enemy: Enemy):
    game.enemies_group.add(enemy)
    
def spawn_random_enemy(game):
    spawn_enemy(game, Zombie1((500,300), constants.ZOMBIE_1))

def enemies_movement(game, enemies: list[Enemy]):
    """Handles the movement of the enemies.
    """
    
    player_pos: vec = vec(game.player.rect.center)
    
    def flip():
        e.image = pygame.transform.flip(e.image, True, False)
        e.last_dir = e.dir.copy()
    
    _flip_margin = 10
        
    for e in enemies:
        
        if player_pos.x < e.rect.centerx - _flip_margin:
            e.dir.x = -1
            if e.last_dir.x > e.dir.x:
                flip()
        elif player_pos.x > e.rect.centerx + _flip_margin:
            e.dir.x = 1
            if e.last_dir.x < e.dir.x:
                flip()
        else:
            e.dir.x = 0
            
        
        
        e.acceleration.x = 0
        e.last_rect = e.rect.copy()
        
            
        # Movement
        if e.dir.x != 0:
            e.acceleration.x = (game.gravity_accelaration/2) * e.dir.x
        
        e.acceleration.x += e.speed.x * game.friction
        e.speed.x += e.acceleration.x
        e.pos.x += e.speed.x + 0.5 * e.acceleration.x
        
        # Gravity
        game.apply_gravity(e)
        e.update_rect()
        
        # jump
        _grounded = enemy_collision(game, e, game.jumpable_group, enums.Orientation.VERTICAL)
        if e.dir.y > 0 and _grounded:
            e.speed.y = - e.jump_force
        
        # solid collision
        enemy_collision(game, e, game.collision_group, enums.Orientation.HORIZONTAL)

def enemy_collision(game, enemy: Enemy, targets: pygame.sprite.Group, direction: enums.Orientation):
        """Handles collision between the enemy and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the enemy was moving.
        """
        collision_objs = pygame.sprite.spritecollide(enemy, targets, False)
        if collision_objs:
            game.collision(enemy, collision_objs, direction)
            return True
        return False