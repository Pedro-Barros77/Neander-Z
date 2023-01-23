import pygame, math as maths, datetime, random

from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller, menu_controller as mc, resources
from domain.content.weapons.semi_auto import SemiAuto
from domain.content.weapons.shotgun import Shotgun
from domain.content.weapons.full_auto import FullAuto
from domain.content.weapons.melee import Melee
from domain.content.weapons.launcher import Launcher
from domain.content.weapons.sniper import Sniper
from domain.models.weapon import Weapon
from domain.models.progress_bar import ProgressBar
from domain.models.rectangle_sprite import Rectangle
from domain.models.backpack import BackPack
from domain.models.ui.popup_text import Popup

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, character: enums.Characters, **kwargs):
        super().__init__()
        self.character: enums.Characters = character
        """Name of the character."""
        self.net_id = kwargs.pop("net_id", 0)
        """The ID of this player in the network."""
        self.jump_force = kwargs.pop("jump_force", 9)
        """The force of the player for jumping."""
        self.movement_speed = kwargs.pop("movement_speed", 0.49)
        self.start_movement_speed = self.movement_speed
        """The movement speed of the player."""
        self.max_health = kwargs.pop("max_health", 100)
        """The maximum health of the player."""
        self.health = kwargs.pop("health", self.max_health)
        """The current health of the player."""
        self.stamina = kwargs.pop("stamina", 800)
        """The stamina of the player. Drains when running, jumping and attacking."""
        self.max_stamina = self.stamina
        self.stamina_regen_delay_ms = kwargs.pop("stamina_regen_delay_ms", 1000)
        self.stamina_regen_rate = kwargs.pop("stamina_regen_rate", 3)
        self.sprint_stamina_drain = kwargs.pop("run_stamina_drain", 3)
        self.jump_stamina_drain = kwargs.pop("jump_stamina_drain", 4)
        self.attack_stamina_drain = kwargs.pop("attack_stamina_drain", 1)
        self.last_stamina_use = datetime.datetime.now()

        self.score = 0
        """The amount of points of the player""" 

        self.money = 0
        """The amount of money of the player""" 
        
        self.name = kwargs.pop("name", "player")
        """The name of this object, for debugging."""
        
        self.is_alive = True
        """If the player is still alive."""
        
        self.sprinting = False
        self.sprint_speed_weight = kwargs.pop("sprint_speed_weight", 0.95)
        self.sprint_speed_multiplier = kwargs.pop("sprint_speed_multiplier", (self.sprint_speed_weight*0.7) / self.movement_speed) #(self.sprint_speed_weight*0.7) / self.movement_speed
        
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
        
        self.image = game_controller.scale_image(pygame.image.load(resources.get_character_path(self.character, enums.AnimActions.IDLE)), self.image_scale, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The surface of the player."""
        	
        self.rect = self.image.get_rect()
        """The rect of the player."""
        self.rect.topleft = self.pos
        
        self.offset_camera = vec(0,0)
        """The adjustment that every object should do to their position so the camera is centered on the player."""
        
        self.last_rect = self.rect.copy()
        """The rect of the player on the previous frame."""
        
        self.player2_mouse_pos: vec = vec(0,0)
        """The mouse position of the other player."""
        self.player2_rect: pygame.Rect = pygame.Rect(0,0,1,1)
        
        self.upgrades_map: dict = kwargs.pop("upgrades_map", None)
        """Upgrades that the player bought for this character."""
        
        self.backpack = BackPack()
        
        self.current_weapon: Weapon = None
        """The weapon on player's hand."""

        self.add_weapon(enums.Weapons.MACHETE)
        
        """Time in milliseconds to wait since last weapon switch to be able to switch again."""
        self.last_weapon_switch: datetime.datetime = datetime.datetime.now()
        
        self.turning_dir = 0
        """The directino that tha player is turning to (left: -1, right: 1)."""
        self.turning_frame = 0
        """The current frame index of the turning animation."""
        turn_folder = resources.get_character_path(self.character, enums.AnimActions.TURN)
        self.turn_frames = game_controller.load_sprites(turn_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The frames of the turning animation."""
        
        self.jumping_sideways = False
        """If the jumping animation is running."""
        self.jumping_frame = 0
        """The current frame index of the jumping animation."""
        jump_folder = resources.get_character_path(self.character, enums.AnimActions.JUMP)
        self.jump_frames = game_controller.load_sprites(jump_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The frames of the jumping animation."""
        self.jump_frames.append(self.jump_frames[-1])
        self.jumping = False
        
        self.running = False
        """If the running animation is running."""
        self.running_frame = 0
        """The current frame index of the running animation."""
        run_folder = resources.get_character_path(self.character, enums.AnimActions.RUN)
        self.run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The frames of the running animation."""
        
        self.falling_ground = False
        """If the falling ground animation is running."""
        self.falling_ground_frame = 0
        """The current frame index of the falling ground animation."""
        fall_ground_folder = resources.get_character_path(self.character, enums.AnimActions.FALL_GROUND)
        self.fall_ground_frames = game_controller.load_sprites(fall_ground_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        """The frames of the falling ground animation."""
        
        self.changing_weapon = False
        """If the weapon change animation is running."""
        
        _grave_scale = 0.3
        self.grave_dropping = False
        """If the gravestone blood dropping animation is running."""
        self.grave_drop_frame = 0
        """The current frame index of the gravestone blood dropping."""
        self.grave_blood_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}items\\grave_stone_blood', _grave_scale, enums.ConvertType.CONVERT_ALPHA)
        """The frames of the gravestone blood dropping animation."""
        self.grave_stone_frame = game_controller.scale_image(pygame.image.load(f'{resources.IMAGES_PATH}items\\grave_stone.png'), _grave_scale, enums.ConvertType.CONVERT_ALPHA)
        """The gravestone image without blood."""
        
        self.health_bar: ProgressBar = None
        """The health bar of the player."""
        self.stamina_bar = ProgressBar(self.max_stamina, pygame.Rect((self.rect.left, self.rect.top), (self.rect.width * 1.3, 6)), border_width = 1, bar_color = colors.YELLOW,use_animation = False)
        """The health bar of the player."""
        
        self.survived_wave = 0
        
        _feet_rect = self.rect.copy()
        _feet_rect.width *= 0.3
        _feet_rect.height = self.rect.height
        self.feet_collider = Rectangle(_feet_rect.size, _feet_rect.topleft)
        
        self.player2_offset = vec(0,0)
        
        self.is_player1 = self.name == "P1"
        self.jump_sounds = pygame.mixer.Sound(resources.get_player_sfx(self.character, enums.AnimActions.JUMP))
        self.fall_sound = pygame.mixer.Sound(resources.get_player_sfx(self.character, enums.AnimActions.FALL_GROUND))
        self.damage_sounds = game_controller.load_sounds(resources.get_player_sfx(self.character, enums.AnimActions.TAKE_DAMAGE), 0.5)

        self.reload_popup: Popup = None
        
        if self.is_player1:
            self.health_bar = ProgressBar(self.max_health, pygame.Rect((10, 10), (game_controller.screen_size.x/2, 20)), hide_on_full = False)
        else:
            self.health_bar = ProgressBar(self.max_health, pygame.Rect((self.rect.left, self.rect.top), (self.rect.width * 1.3, 8)), border_width = 1)
    
    def change_weapon(self, slot: int = None):
        _now = datetime.datetime.now()
        if self.last_weapon_switch + datetime.timedelta(milliseconds=self.current_weapon.weapon_switch_ms) > _now:
            return False
        
        if type(self.backpack.equipped_primary) != type(self.backpack.equipped_secondary):
            return False
        
        self.last_weapon_switch = _now
        self.changing_weapon = True
        self.current_weapon.changing_weapon = True
        
        if slot == None:
            slot = 1 if self.current_weapon.weapon_type == self.backpack.equipped_primary else 0
            
            
        match slot:
            case 0:
                w = self.backpack.get_weapon(self.backpack.equipped_primary)
                if w:
                    self.current_weapon = w
                    return True
            case 1:
                w = self.backpack.get_weapon(self.backpack.equipped_secondary)
                if w:
                    self.current_weapon = w
                    return True
        
        return False
    
    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)
        
    def update_feet(self):
        self.feet_collider.rect.centerx = self.rect.centerx
        self.feet_collider.rect.bottom = self.rect.bottom + 5
        
    def load_state(self, state: dict):
        self.character = state["character"]
        self.max_health = state["max_health"]
        self.health = self.max_health
        self.health_bar.set_max_value(self.max_health)
        self.health_bar.set_value(self.max_health)
        self.movement_speed = state["movement_speed"]
        self.start_movement_speed = self.movement_speed
        self.jump_force = state["jump_force"]
    
    # called each frame
    def update(self, **kwargs):
        if not self.is_alive:
            self.grave_stone_anim(0.2)
            return
            
        group_name = kwargs.pop("group_name", "")
        if group_name == "jumpable":
            return
        game = kwargs.pop("game", None)
        
        self.movement(game)
        _now = datetime.datetime.now()
        
        if self.sprinting:
            self.movement_speed = self.start_movement_speed * self.sprint_speed_multiplier
            self.stamina_bar.remove_value(self.sprint_stamina_drain * mc.dt)
            self.last_stamina_use = _now
        else:
            self.movement_speed = self.start_movement_speed 
            
        if self.jumping and self.speed.y < 0:
            self.stamina_bar.remove_value(self.jump_stamina_drain * mc.dt)
            self.last_stamina_use = _now
        
        _is_melee = self.current_weapon.fire_mode == enums.FireMode.MELEE
        if _is_melee and self.stamina < self.attack_stamina_drain:
            self.current_weapon.has_stamina = False
        elif self.stamina >= self.attack_stamina_drain:
            self.current_weapon.has_stamina = True
            
        _attacking = _is_melee and self.current_weapon.firing
        
        if _attacking:
            self.stamina_bar.remove_value((self.attack_stamina_drain + self.current_weapon.stamina_use) * mc.dt)
            self.last_stamina_use = _now

        if not self.sprinting and not self.jumping and not _attacking and _now > self.last_stamina_use + datetime.timedelta(milliseconds=self.stamina_regen_delay_ms):
            self.stamina_bar.add_value(self.stamina_regen_rate * mc.dt)
            
        self.stamina = self.stamina_bar.value
            
        
        self.health_bar.update()
        self.stamina_bar.update()
        self.current_weapon.update()
        
        if self.is_player1:
            _mouse_target = vec(pygame.mouse.get_pos())
            _offset_camera_target = self.offset_camera
        else:
            _mouse_target = self.player2_mouse_pos
            _offset_camera_target = vec(0,0)
            self.health_bar.rect.centerx = self.rect.centerx
            self.health_bar.rect.top = self.rect.top - 15
            
        self.stamina_bar.rect.centerx = self.rect.centerx
        self.stamina_bar.rect.top = self.rect.top - 15

        #region Weapon Animation
        
        def flip():
            self.current_weapon.current_frame = pygame.transform.flip(self.current_weapon.current_frame, False, True)
            self.current_weapon.last_dir = self.current_weapon.dir
            
        if game.focused:
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
        
        _weapon_center: vec = self.current_weapon.weapon_anchor + self.rect.topleft - _offset_camera_target
        
        if self.is_player1 and game.focused and not self.changing_weapon:
            self.current_weapon.weapon_aim_angle = game_controller.angle_to_mouse(_weapon_center, _mouse_target)
        
        # Weapon pos
        self.current_weapon.rect.center = game_controller.point_to_angle_distance(_weapon_center, self.current_weapon.weapon_distance, -maths.radians(self.current_weapon.weapon_aim_angle)) + self.current_weapon.barrel_offset
        # Weapon rotation
        self.current_weapon.image, self.current_weapon.rect = game_controller.rotate_to_angle(self.current_weapon.current_frame, vec(self.current_weapon.rect.center),self.current_weapon.weapon_aim_angle)
        
        #endregion Weapon Animation
        
        #region Animation Triggers
        
        if self.turning_dir != 0:
            self.turn_anim(0.3 * mc.dt)
        if self.falling_ground:
            self.fall_ground_anim(0.2 * mc.dt)
        if self.running:
            self.run_anim(abs(self.speed.x / 26.4) * mc.dt)
        if self.jumping_sideways:
            self.jump_anim(0.2 * mc.dt)
        if self.changing_weapon:
            self.change_weapon_anim()
            
        #endregion Animation Triggers
        

        return
        
    def draw(self, surface: pygame.Surface, offset: vec):
        if not self.is_alive:
            self.draw_grave_stone(surface, offset)
            return
        
        
        surface.blit(self.image, self.pos - offset)
        _target_offset = offset if not self.is_player1 else vec(0,0)
        
        self.current_weapon.draw(surface, offset)
        
        #popup
        if self.current_weapon.magazine_bullets == 0:
            if self.reload_popup == None:
                self.reload_popup = Popup("Reload: R", vec(self.rect.centerx, self.rect.top - 50) - _target_offset, name="Reload: R", unique= True, **constants.POPUPS["blink"])
                mc.popup(self.reload_popup)
            else:
                self.reload_popup.rect.centerx = self.rect.centerx - self.offset_camera.x
                self.reload_popup.rect.bottom = self.rect.top - 10 - self.offset_camera.y
                if self.backpack.get_ammo(self.current_weapon.bullet_type) == 0:
                    self.reload_popup.text = "No ammo!"
        elif self.reload_popup != None:
           self.reload_popup.destroy()
           self.reload_popup = None
        
        if not self.is_player1:
            self.health_bar.draw(surface, _target_offset)
            
        self.stamina_bar.draw(surface, self.offset_camera)
        
            
        # pygame.draw.rect(surface, colors.BLUE, math.rect_offset(self.feet_collider.rect, -offset), 3)
        
    
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
        self.sprinting = pygame.K_LSHIFT in game.pressed_keys and self.running and self.stamina > self.sprint_stamina_drain
            
        # Move right
        if pressing_right:
            # pressing right but not left
            if not pressing_left:
                self.acceleration.x = round(self.movement_speed, 6)
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
                self.running = False
                self.turning_dir = -1
            
        # Move left
        if pressing_left:
            # pressing left but not right
            if not pressing_right:
                self.acceleration.x = round(-self.movement_speed, 6)
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
                self.running = False
                self.turning_dir = -1
            
        # Movement
        self.acceleration.x = round(self.acceleration.x + self.speed.x * game.friction, 6)
        self.speed.x += round(self.acceleration.x * mc.dt, 6)
        self.pos.x += (self.speed.x + 0.5 * self.acceleration.x) * mc.dt
        
        # Gravity
        game.apply_gravity(self)
        self.update_rect()
        self.update_feet()
        
        
        # jump
        _was_grounded = self.grounded
        self.grounded = self.collision(game, game.jumpable_group, enums.Orientation.VERTICAL, self.feet_collider)
        if not _was_grounded and self.grounded:
            self.jumping_sideways = False
            self.jumping = False
            self.falling_ground = True
            self.fall_sound.play()
            if pressing_left != pressing_right:
                self.running = True
        
        if (pygame.K_SPACE in game.pressed_keys or pygame.K_w in game.pressed_keys) and self.grounded and self.stamina > self.jump_stamina_drain:
            self.speed.y = -self.jump_force
            self.jump_sounds.play()
            self.jumping = True
            if pressing_left != pressing_right:
                self.falling_ground = False
                self.running = False
                self.jumping_sideways = True
                
            if pygame.K_SPACE in game.pressed_keys:
                game.pressed_keys.remove(pygame.K_SPACE)
            elif pygame.K_w in game.pressed_keys:
                game.pressed_keys.remove(pygame.K_w)
    
        # solid collision
        self.collision(game, game.collision_group, enums.Orientation.HORIZONTAL)
        self.update_feet()
        
    def collision(self, game, targets: pygame.sprite.Group, direction: enums.Orientation, obj = None):
        """Handles collision between the player and collidable objects.

        Args:
            targets (pygame.sprite.Group | list[pygame.sprite.Sprite])
            direction (enums.Orientation): The direction that the player was moving.
        """
        if obj == None:
            obj = self
        collision_objs = pygame.sprite.spritecollide(obj, targets, False)
        if collision_objs:
            game.collision(self, collision_objs, direction)
            return True
        return False    
    
        
    def shoot(self, **kwargs):
        _bullet_pos = game_controller.point_to_angle_distance(self.current_weapon.weapon_anchor + self.rect.topleft + vec(0,self.current_weapon.bullet_spawn_offset.y), self.current_weapon.bullet_spawn_offset.x, -maths.radians(self.current_weapon.weapon_aim_angle))
        return self.current_weapon.shoot(_bullet_pos, self.net_id, **kwargs)
    
    def reload_weapon(self):
        return self.current_weapon.reload()
   
                    
    def turn_anim(self, speed: float):
        self.turning_frame = math.clamp(self.turning_frame + (speed * self.turning_dir), 0, len(self.turn_frames)-1)
        
        if self.turning_frame == len(self.turn_frames)-1:
            self.running = True if self.turning_dir != 0 else False
            self.turning_dir = 0
        self.image = game_controller.scale_image(self.turn_frames[int(self.turning_frame)], self.image_scale)
        if self.turning_dir > 0 and self.acceleration.x > 0 or\
           self.turning_dir < 0 and self.acceleration.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def change_weapon_anim(self):
        now = datetime.datetime.now()
        start = self.last_weapon_switch
        end = self.last_weapon_switch + datetime.timedelta(milliseconds=self.current_weapon.weapon_switch_ms)
        
        if end < now:
            self.changing_weapon = False
            self.current_weapon.changing_weapon = False
            return
        
        percentage = ((now - start) / (end - start)) * 100
        percentage = math.clamp(percentage, 0, 100)
        
        angle = 0
        if self.current_weapon.dir > 0:
            angle = ((90*(100-percentage))/100)
        else:
            angle = 90+(90-((90*(100-percentage))/100))
            
        
        self.current_weapon.weapon_aim_angle = angle
            
    def jump_anim(self, speed: float):
        if self.jumping_frame > len(self.jump_frames)-1:
            self.jumping_frame = 0
            self.jumping_sideways = False
        self.image = game_controller.scale_image(self.jump_frames[int(self.jumping_frame)], self.image_scale)
        if self.speed.x > 0:
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
        if self.speed.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def take_damage(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health - value, 0, self.health_bar.max_value)
        self.health_bar.remove_value(value)
        
        if self.is_player1:
            mc.popup(Popup(f'-{round(value,2)}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera, **constants.POPUPS["damage"]))
        else:
            mc.popup(Popup(f'-{round(value,2)}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera - self.player2_offset, **constants.POPUPS["damage"]))

        rand_sound = random.randint(0, len(self.damage_sounds)-1)
        self.damage_sounds[rand_sound].play()

        if self.health == 0:
            self.kill()        
        
    def get_health(self, value: float):
        if value < 0:
            return
        self.health = math.clamp(self.health + value, 0, self.health_bar.max_value)
        self.health_bar.add_value(value)
        mc.popup(Popup(f'+{value}', self.pos + vec(self.rect.width / 2 - 20,-30) - self.offset_camera - self.player2_offset, **constants.POPUPS["health"]))

    def add_weapon(self, weapon_type: enums.Weapons, equip = True):
        existing_weapon = self.backpack.get_weapon(weapon_type)
        if existing_weapon != None:
            return existing_weapon, False
        
        
        weapon = None
        
        default_weapon_distance = self.rect.width/2 + 30
        default_weapon_anchor = vec(self.rect.width/2, self.rect.height/3)
        
        match weapon_type:
            case enums.Weapons.P_1911:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.DEAGLE:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = self.rect.width/2 + 30, backpack = self.backpack)
            case enums.Weapons.SHORT_BARREL:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.UZI:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.MACHETE:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = self.rect.width/2 + 20, backpack = self.backpack)
            case enums.Weapons.RPG:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = self.rect.width/2 + 20, backpack = self.backpack)
            case enums.Weapons.SV98:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.M16:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = self.rect.width/2 + 20, backpack = self.backpack)
            case enums.Weapons.P_93R:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.SCAR:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
            case enums.Weapons.DEBUG:
                weapon = constants.get_weapon(weapon_type, vec(self.rect.width, self.rect.centery), weapon_anchor = default_weapon_anchor, weapon_distance = default_weapon_distance, backpack = self.backpack)
                weapon_type = enums.Weapons.SCAR
            
        if weapon == None:
            return None, False
        
        if weapon.is_primary:
            self.backpack.primary_weapons.append(weapon)
        else:
            self.backpack.secondary_weapons.append(weapon)
            
        if equip:
            self.backpack.equip_weapon(weapon_type)
            if weapon.is_primary:
                self.current_weapon = self.backpack.get_weapon(self.backpack.equipped_primary)
            else:
                self.current_weapon = self.backpack.get_weapon(self.backpack.equipped_secondary)
        
        return weapon, True
    
    def grave_stone_anim(self, speed: float):
        self.grave_drop_frame += speed
        
        if self.grave_drop_frame > len(self.grave_blood_frames)-1:
            self.grave_drop_frame = 0
        self.image = self.grave_blood_frames[int(self.grave_drop_frame)]
        
    def draw_grave_stone(self, screen: pygame.Surface, offset: vec):
        _grave_rect = self.grave_stone_frame.get_rect()
        _grave_rect.centerx = self.rect.centerx - offset.x
        _grave_rect.bottom = self.rect.bottom - offset.y
        
        txt_player_name = mc.get_text_surface(str(self.character.value).upper(), colors.MEDIUM_GRAY, resources.px_font(13))
        player_name_rect = txt_player_name.get_rect()
        player_name_rect.centerx = _grave_rect.centerx
        player_name_rect.bottom = _grave_rect.centery
        
        if self.survived_wave == 0:
            waves_text = f'WAV 1'
        else:
            waves_text = f'WAV 1-{self.survived_wave}'
            
        txt_wave = mc.get_text_surface(waves_text, colors.MEDIUM_GRAY, resources.px_font(11))
        wave_rect = txt_wave.get_rect()
        wave_rect.centerx = _grave_rect.centerx
        wave_rect.top = player_name_rect.bottom + 5
            
        
        screen.blit(self.grave_stone_frame, _grave_rect)
        screen.blit(txt_player_name, player_name_rect)
        screen.blit(txt_wave, wave_rect)
        screen.blit(self.image, _grave_rect)
    
    def kill(self):
        self.is_alive = False
        self.grave_dropping = True     