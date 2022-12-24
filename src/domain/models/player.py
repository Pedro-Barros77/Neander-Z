import pygame, math as maths

from pygame.math import Vector2 as vec


from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller, menu_controller
from domain.content.weapons.pistol import Pistol
from domain.models.progress_bar import ProgressBar
from domain.content.weapons.small_bullet import SmallBullet
from domain.models.ui.popup_text import Popup




class Player(pygame.sprite.Sprite):
    def __init__(self, pos, character: enums.Characters, **kwargs):
        super().__init__()
        self.character: enums.Characters = character
        """Name of the character."""
        self.net_id = kwargs.pop("net_id", 0)
        """The ID of this player in the network."""
        self.jump_force = kwargs.pop("jump_force", 12)
        """The force of the player for jumping."""
        self.movement_speed = kwargs.pop("movement_speed", 0.5)
        """The movement speed of the player."""
        self.health = 100
        """The current health of the player."""
        self.max_health = self.health
        """The maximum health of the player."""

        self.score = 0
        """The amount of points of the player""" 

        self.money = 0
        """The amount of money of the player""" 
        
        self.name = kwargs.pop("name", "player")
        """The name of this object, for debugging."""
        
        self.pos: vec = vec((pos))
        """The X and Y position coordinates of the player."""
        self.speed = kwargs.pop("speed", vec(0,0))
        """The current X and Y movement speed of the player."""
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        """How much the player is accelerating (gaining speed) over time."""
        self.grounded = False
        """If the player is touching the ground (or any jumpable object)."""
        self.image_scale = 2
        """How much the image will be scaled from original file."""
        
        self.image = game_controller.scale_image(pygame.image.load(constants.get_character_frames(self.character, enums.AnimActions.IDLE)), self.image_scale)
        """The surface of the player."""
        	
        self.rect = self.image.get_rect()
        """The rect of the player."""
        self.rect.topleft = self.pos
        
        self.offset_camera = vec(0,0)
        """The adjustment that every object should do to their position so the camera is centered on the player."""
        
        self.last_rect = self.rect.copy()
        """The rect of the player on the previous frame."""
        
        self.weapon_aim_angle: float = 0
        """The angle that the container is rotated along with the weapon."""
        self.player2_mouse_pos: vec = vec(0,0)
        """The mouse position of the other player."""
        self.player2_rect: pygame.Rect = pygame.Rect(0,0,1,1)
        
        self.firing = False
        """If the weapon firing animation is running."""
        self.current_weapon = Pistol((self.rect.width, self.rect.centery), fire_frames_path = constants.PISTOL_FOLDER)
        """The weapon on player's hand."""
        
        self.turning_dir = 0
        """The directino that tha player is turning to (left: -1, right: 1)."""
        self.turning_frame = 0
        """The current frame index of the turning animation."""
        turn_folder = constants.get_character_frames(self.character, enums.AnimActions.TURN)
        self.turn_frames = game_controller.load_sprites(turn_folder)
        """The frames of the turning animation."""
        
        self.jumping = False
        """If the jumping animation is running."""
        self.jumping_frame = 0
        """The current frame index of the jumping animation."""
        jump_folder = constants.get_character_frames(self.character, enums.AnimActions.JUMP)
        self.jump_frames = game_controller.load_sprites(jump_folder)
        """The frames of the jumping animation."""
        self.jump_frames.append(self.jump_frames[-1])
        
        self.running = False
        """If the running animation is running."""
        self.running_frame = 0
        """The current frame index of the running animation."""
        run_folder = constants.get_character_frames(self.character, enums.AnimActions.RUN)
        self.run_frames = game_controller.load_sprites(run_folder)
        """The frames of the running animation."""
        
        self.falling_ground = False
        """If the falling ground animation is running."""
        self.falling_ground_frame = 0
        """The current frame index of the falling ground animation."""
        fall_ground_folder = constants.get_character_frames(self.character, enums.AnimActions.FALL_GROUND)
        self.fall_ground_frames = game_controller.load_sprites(fall_ground_folder)
        """The frames of the falling ground animation."""
        
        self.weapon_anchor = vec(self.rect.width/2, self.rect.height/3)
        """The anchor point of the weapon (the center of the circle it orbits around), relative to the player position"""
        
        self.health_bar: ProgressBar = None
        """The health bar of the player."""
        
        self.player2_offset = vec(0,0)
        
        self.is_player1 = self.name == "P1"
        
        if self.is_player1:
            self.health_bar = ProgressBar(self.health, pygame.Rect((10, 10), (game_controller.screen_size.x/2, 20)), hide_on_full = False)
        else:
            self.health_bar = ProgressBar(self.health, pygame.Rect((self.rect.left, self.rect.top), (self.rect.width * 1.3, 8)), border_width = 1)
        
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
        
    def load_state(self, state: dict):
        self.character = state["character"]
        self.max_health = state["max_health"]
        self.movement_speed = state["movement_speed"]
        self.jump_force = state["jump_force"]
    
    # called each frame
    def update(self, **kwargs):
        group_name = kwargs.pop("group_name", "")
        if group_name == "jumpable":
            return
        game = kwargs.pop("game", None)
        
        self.movement(game)
        
        self.health_bar.update()
        
        if self.is_player1:
            _mouse_target = vec(pygame.mouse.get_pos())
            _offset_camera_target = self.offset_camera
        else:
            _mouse_target = self.player2_mouse_pos
            _offset_camera_target = vec(0,0)
            self.health_bar.rect.centerx = self.rect.centerx
            self.health_bar.rect.top = self.rect.top - 15

        #region Weapon Animation
        
        def flip():
            self.current_weapon.current_frame = pygame.transform.flip(self.current_weapon.current_frame, False, True)
            self.current_weapon.last_dir = self.current_weapon.dir
            
        if _mouse_target.x < self.rect.centerx - _offset_camera_target.x:
            self.current_weapon.dir = -1
            if self.current_weapon.last_dir > self.current_weapon.dir:
                flip()
        elif _mouse_target.x > self.rect.centerx- _offset_camera_target.x:
            self.current_weapon.dir = 1
            if self.current_weapon.last_dir < self.current_weapon.dir:
                flip()
        else:
            self.current_weapon.dir = 0
        
        
        _weapon_center: vec = self.weapon_anchor + self.rect.topleft - _offset_camera_target
        
        if self.is_player1:
            self.weapon_aim_angle = game_controller.angle_to_mouse(_weapon_center, _mouse_target)
        
        # The distance from the weapon anchor to position the weapon
        _weapon_distance = self.rect.width/2 + 30
        # Weapon pos
        self.current_weapon.rect.center = game_controller.point_to_angle_distance(_weapon_center, _weapon_distance, -maths.radians(self.weapon_aim_angle)) + self.current_weapon.barrel_offset
        # Weapon rotation
        self.current_weapon.image, self.current_weapon.rect = game_controller.rotate_to_angle(self.current_weapon.current_frame, vec(self.current_weapon.rect.center),self.weapon_aim_angle)
        
        #endregion Weapon Animation
        
        #region Animation Triggers
        
        if self.turning_dir != 0:
            self.turn_anim(0.3)
        if self.falling_ground:
            self.fall_ground_anim(0.2)
        if self.running:
            self.run_anim(abs(self.speed.x / 26.4))
        if self.jumping:
            self.jump_anim(0.2)
        if self.firing:
            self.firing = self.current_weapon.fire_anim()
            
        #endregion Animation Triggers
        

        return
        
    def draw(self, surface: pygame.Surface, offset: vec):
        surface.blit(self.image, self.pos - offset)
        _target_offset = offset if not self.is_player1 else vec(0,0)
        
        surface.blit(self.current_weapon.image, vec(self.current_weapon.rect.topleft) - _target_offset)
        self.health_bar.draw(surface, _target_offset)
        
    
    def movement(self, game):
        """Handles the movement of player 1.
        """
        if not self.is_player1:
            return
        self.last_rect = self.rect.copy()
        self.acceleration.x = 0
            
        pressing_right = pygame.K_d in game.pressed_keys
        pressing_left = pygame.K_a in game.pressed_keys
        was_pressing_right = pygame.K_d in game.last_pressed_keys
        was_pressing_left = pygame.K_a in game.last_pressed_keys
            
        # Move right
        if pressing_right:
            # pressing right but not left
            if not pressing_left:
                self.acceleration.x = self.movement_speed
                # was pressing both left and right, but released left
                if was_pressing_left and was_pressing_right:
                    self.running = False
                    self.turning_dir = 1
            # started to press right
            if not was_pressing_right:
                self.turning_dir = 1
            # started to press left and right
            if pressing_left:
                self.running = False
                self.turning_dir = -1
        elif was_pressing_right:
                self.running = 0
                self.turning_dir = -1
            
        # Move left
        if pressing_left:
            # pressing left but not right
            if not pressing_right:
                self.acceleration.x = -self.movement_speed
                # was pressing both left and right, but released right
                if was_pressing_left and was_pressing_right:
                    self.running = False
                    self.turning_dir = 1
            # started to press left
            if not was_pressing_left:
                self.turning_dir = 1
            # pressing left and right
            if pressing_right:
                self.running = False
                self.turning_dir = -1
        elif was_pressing_left and not pressing_right:
                self.running = 0
                self.turning_dir = -1
            
        # Movement
        self.acceleration.x += self.speed.x * game.friction
        self.speed.x += self.acceleration.x
        self.pos.x += self.speed.x + 0.5 * self.acceleration.x
        
        # Gravity
        game.apply_gravity(self)
        self.update_rect()
        
        # jump
        _was_grounded = self.grounded
        _old_pos = self.pos.y
        self.grounded = self.collision(game, game.jumpable_group, enums.Orientation.VERTICAL)
        if not _was_grounded and self.grounded and abs(_old_pos - self.pos.y) > 2 :
            self.jumping = False
            self.falling_ground = True
            if pressing_left != pressing_right:
                self.running = True
        
        if pygame.K_SPACE in game.pressed_keys and self.grounded:
            self.speed.y = -self.jump_force
            if pressing_left != pressing_right:
                self.falling_ground = False
                self.running = False
                self.jumping = True
           
            game.pressed_keys.remove(pygame.K_SPACE)
    
        # solid collision
        self.collision(game, game.collision_group, enums.Orientation.HORIZONTAL)
        
    def collision(self, game, targets: pygame.sprite.Group, direction: enums.Orientation):
        """Handles collision between the player and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the player was moving.
        """
        collision_objs = pygame.sprite.spritecollide(self, targets, False)
        if collision_objs:
            game.collision(self, collision_objs, direction)
            return True
        return False    
    
        
    def shoot(self):
        self.firing = True
        _bullet_pos = game_controller.point_to_angle_distance(self.weapon_anchor + self.rect.topleft, self.rect.width/2 + 5, -maths.radians(self.weapon_aim_angle))
        
        return SmallBullet(_bullet_pos, self.weapon_aim_angle, 30, self.current_weapon.damage, self.net_id, game_controller.get_bullet_id())
    
    
                    
    def turn_anim(self, speed: float):
        self.turning_frame = math.clamp(self.turning_frame + (speed * self.turning_dir), 0, len(self.turn_frames)-1)
        
        if self.turning_frame == len(self.turn_frames)-1:
            self.running = True if self.turning_dir != 0 else False
            self.turning_dir = 0
        self.image = game_controller.scale_image(self.turn_frames[int(self.turning_frame)], self.image_scale)
        if self.turning_dir > 0 and self.acceleration.x > 0 or\
           self.turning_dir < 0 and self.acceleration.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def jump_anim(self, speed: float):
        if self.jumping_frame > len(self.jump_frames)-1:
            self.jumping_frame = 0
            self.jumping = False
        self.image = game_controller.scale_image(self.jump_frames[int(self.jumping_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.jumping_frame += speed
    
    def fall_ground_anim(self, speed: float):
        if self.falling_ground_frame > len(self.fall_ground_frames)-1:
            self.image = game_controller.scale_image(self.fall_ground_frames[int(len(self.fall_ground_frames)-1)], self.image_scale)
            self.falling_ground_frame = 0
            self.falling_ground = False
            return
        self.image = game_controller.scale_image(self.fall_ground_frames[int(self.falling_ground_frame)], self.image_scale)
        self.falling_ground_frame += speed
        
    def run_anim(self, speed: float):
        self.running_frame += speed
        
        if self.running_frame > len(self.run_frames):
            self.running_frame = 0
        self.image = game_controller.scale_image(self.run_frames[int(self.running_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def take_damage(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health - value, 0, self.health_bar.max_value)
        self.health_bar.remove_value(value)
        
        
        if self.is_player1:
            menu_controller.popup(Popup(f'-{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera, **constants.POPUPS["damage"]))
        else:
            menu_controller.popup(Popup(f'-{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera - self.player2_offset, **constants.POPUPS["damage"]))
        
        
    def get_health(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health + value, 0, self.health_bar.max_value)
        self.health_bar.add_value(value)
        menu_controller.popup(Popup(f'+{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera - self.player2_offset, **constants.POPUPS["health"]))