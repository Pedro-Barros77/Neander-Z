import pygame, datetime, random
from pygame.math import Vector2 as vec

from domain.utils import colors, constants, enums, math_utillity as math
from domain.services import game_controller, menu_controller as mc, resources, assets_manager
from domain.models.ui.popup_text import Popup
from domain.models.enemy import Enemy
from domain.models.rectangle_sprite import Rectangle





class ZRaimundo(Enemy):
    def __init__(self, pos, wave, assets_manager: assets_manager.AssetsManager, **kwargs):
        kwargs["image_scale"] = 1.1
        super().__init__(pos, enums.Enemies.Z_RAIMUNDO,wave, assets_manager, **kwargs)
        
        
        self.damage = kwargs.pop("damage", 15)
        self.name = kwargs.pop("name", f"zombie_1")
        self.jump_force = kwargs.pop("jump_force", 12)
        
        self.pos: vec = vec((pos))
        self.speed = kwargs.pop("speed", vec(0,0))
        self.acceleration: vec = kwargs.pop("acceleration", vec(0,0))
        self.dir: vec = vec(-1,0)
        self.last_frame_dir = self.dir.copy()
        self.attack_distance = kwargs.pop("attack_distance", 30)
        self.hit_frame = 8
        self.hiting = False
        self.attack_box = vec(30,30)
        self.hit_rectangle = None
        self.head_shot_multiplier = kwargs.pop("head_shot_multiplier", 2)
        
        _health_rect = self.health_bar.rect.copy()
        _health_rect.width = self.rect.width * 0.6
        self.health_bar.set_rect(_health_rect)
        
        self.kill_score = kwargs.pop("kill_score", 80)
        self.headshot_score_multiplier = kwargs.pop("headshot_score_multiplier", 2)
        
        self.body_damage_multiplier = kwargs.pop("body_damage_multiplier", 0.2)
        
        self.helmet_health = kwargs.pop("helmet_health", self.health)
        self.start_helmet_health = self.helmet_health
        self.helmet_stage = 0
        self.helmet_break_pos: vec = None
        self.helmet_break_time: datetime.datetime = None
        self.helmet_timeout_ms = kwargs.pop("helmet_timeout_ms", 2000)
        self.helmet_alpha = 255
        
        self.breaking_helmet = False
        self.helmet_frame = 0
        
        
        # run_folder = resources.get_enemy_path(self.enemy_name, enums.AnimActions.RUN)
        # self.run_frames_1 = game_controller.load_sprites(run_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.run_frames_2 = game_controller.load_sprites(run_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.run_frames_3 = game_controller.load_sprites(run_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.run_frames_4 = game_controller.load_sprites(run_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        # attack_folder = resources.get_enemy_path(self.enemy_name, enums.AnimActions.ATTACK)
        # self.attack_frames1 = game_controller.load_sprites(attack_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.attack_frames2 = game_controller.load_sprites(attack_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.attack_frames3 = game_controller.load_sprites(attack_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.attack_frames4 = game_controller.load_sprites(attack_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        # death_folder = resources.get_enemy_path(self.enemy_name, enums.AnimActions.DEATH)
        # self.death_frames1 = game_controller.load_sprites(death_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.death_frames2 = game_controller.load_sprites(death_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.death_frames3 = game_controller.load_sprites(death_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        # self.death_frames4 = game_controller.load_sprites(death_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        # self.helmet_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}enemies\\{str(self.enemy_name.value)}\\helmet_breaking\\', convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        # self.damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.TAKE_DAMAGE), 0.1)
        # self.death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.DEATH), 0.2)
        # self.attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.ATTACK), 0.2)
        # self.helmet_bullet_sounds = game_controller.load_sounds(f'{resources.SOUNDS_PATH}sound_effects\\enemies\\{str(self.enemy_name.value)}\\helmet_bullet_hit\\', 0.2)
        
        self.hitbox_head: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.YELLOW, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, True), name = "zombie_head", id = self.id, owner = self)
        self.hitbox_head.set_rect(pygame.Rect((0,0),(self.hitbox_head.rect.width/4, self.hitbox_head.rect.height - self.rect.height/1.8)))
        self.hitbox_head.rect.centerx = self.rect.centerx
        
        self.hitbox_body: Rectangle = Rectangle(self.rect.size, self.rect.topleft, border_color = colors.GREEN, border_radius = 8, take_damage_callback = lambda value, attacker: self.take_damage(value, attacker, False), name = "zombie_body", id = self.id, owner = self)
        self.hitbox_body.set_rect(pygame.Rect((0,0),(self.hitbox_body.rect.width/3.5, self.hitbox_body.rect.height - self.hitbox_head.rect.height)))
        self.hitbox_body.rect.centerx = self.rect.centerx
 
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        _head_margin = self.rect.width/2.3
        if self.hitbox_head != None:
            match self.dir.x:
                case 1:
                    self.hitbox_head.rect.left = self.rect.left + _head_margin
                case -1:
                    self.hitbox_head.rect.right = self.rect.right - _head_margin
                case 0:
                    self.hitbox_head.rect.right = self.rect.right - _head_margin
                    

        if self.hitbox_body != None:
            self.hitbox_body.rect.centerx = self.rect.centerx
            
        
        self.calculate_helmet_stage()
        
        if int(self.helmet_frame) == len(self.get_helmet_frames())-1:
            self.fade_out_helmet()
        
        if self.running and self.death_time == None:
            self.run_anim(abs(self.speed.x / 5) * mc.dt)
                    
        if self.attacking and self.death_time == None:
            self.attcking_anim(0.2 * mc.dt)
        
        if self.dying and self.death_time == None:
            self.dying_anim(0.2 * mc.dt)
            
        if self.breaking_helmet:
            self.helmet_anim(0.3 * mc.dt)
            

    def draw(self, surface: pygame.Surface, offset: vec): 
        super().draw(surface, offset)
        _now = datetime.datetime.now()
        
        
        
        #helmet
        if self.helmet_break_pos != None and self.helmet_break_time != None and _now < self.helmet_break_time + datetime.timedelta(milliseconds=self.helmet_timeout_ms):
            _helmet = game_controller.scale_image(self.get_helmet_frames()[int(self.helmet_frame)], self.image_scale)
            _result = pygame.Surface(_helmet.get_size(), pygame.SRCALPHA)
            _result.blit(_helmet, (0,0))
            _result.set_alpha(self.helmet_alpha)
            surface.blit(_result, self.helmet_break_pos - offset)


    def fade_out_helmet(self):
        anim_end = (self.helmet_break_time + datetime.timedelta(milliseconds=self.helmet_timeout_ms))
        
        self.helmet_alpha = mc.fade_out_color(colors.WHITE, 255, self.helmet_break_time, anim_end)[3]

    def calculate_helmet_stage(self):
        percentage = self.helmet_health * 100 / self.start_helmet_health
        
        _slice = 100 / 3
        
        if percentage >= _slice * 2:
            self.helmet_stage = 0
        elif percentage >= _slice:
            self.helmet_stage = 1
        elif percentage > 0 and percentage < _slice:
            self.helmet_stage = 2
        else: # <=0
            self.helmet_stage = 3
            
    def get_run_frames(self):
        match self.helmet_stage:
            case 0: return self.assets_manager.get_assets(self.enemy_name, "run_frames_1")
            case 1: return self.assets_manager.get_assets(self.enemy_name, "run_frames_2")
            case 2: return self.assets_manager.get_assets(self.enemy_name, "run_frames_3")
            case 3: return self.assets_manager.get_assets(self.enemy_name, "run_frames_4")
    
    def get_atk_frames(self):
        match self.helmet_stage:
            case 0: return self.assets_manager.get_assets(self.enemy_name, "attack_frames1")
            case 1: return self.assets_manager.get_assets(self.enemy_name, "attack_frames2")
            case 2: return self.assets_manager.get_assets(self.enemy_name, "attack_frames3")
            case 3: return self.assets_manager.get_assets(self.enemy_name, "attack_frames4")
            
    def get_death_frames(self):
        match self.helmet_stage:
            case 0: return self.assets_manager.get_assets(self.enemy_name, "death_frames1")
            case 1: return self.assets_manager.get_assets(self.enemy_name, "death_frames2")
            case 2: return self.assets_manager.get_assets(self.enemy_name, "death_frames3")
            case 3: return self.assets_manager.get_assets(self.enemy_name, "death_frames4")
            
    def get_helmet_frames(self):
        return self.assets_manager.get_assets(self.enemy_name, "helmet_frames")

    def attack(self):
        self.hiting = True
        _rect = pygame.Rect((0,0), self.attack_box)
        _rect.centerx = self.rect.centerx + (10*self.dir.x)
        _rect.centery = self.rect.centery - 20
        self.hit_rectangle = Rectangle(_rect.size, _rect.topleft)
       
        collided = self.attack_collision(self.hit_rectangle)
        if len(collided) > 0:
            for c in collided:
                c.take_damage(self.damage)
            
            rand_sound = random.randint(0, len(self.get_sounds(enums.AnimActions.ATTACK))-1)
            self.get_sounds(enums.AnimActions.ATTACK)[rand_sound].play()
            
            
        
    def run_anim(self, speed: float):
       
        self.run_frame += speed
        if self.run_frame > len(self.get_run_frames())-1:
            self.run_frame = 0
        self.image = game_controller.scale_image(self.get_run_frames()[int(self.run_frame)], self.image_scale)
        if self.speed.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attcking_anim(self, speed: float):
        self.attack_frame += speed
        if int(self.attack_frame) == self.hit_frame - 1 and not self.hiting:
            self.attack()
        if self.attack_frame > len(self.get_atk_frames())-1:
            self.attack_frame = 0
            self.attacking = False
            self.hiting = False
        self.image = game_controller.scale_image(self.get_atk_frames()[int(self.attack_frame)], self.image_scale)
        if self.acceleration.x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def dying_anim(self, speed: float):
        self.death_frame += speed
        if self.death_frame > len(self.get_death_frames())-1:
            self.death_time = datetime.datetime.now()
            self.death_frame = 0
        else:
            self.image = game_controller.scale_image(self.get_death_frames()[int(self.death_frame)], self.image_scale)
        if self.dir.x > 0 and self.death_time == None:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def helmet_anim(self, speed: float):
       
        self.helmet_frame += speed
        if self.helmet_frame > len(self.get_helmet_frames())-1:
            self.breaking_helmet = False
    
        
    def damage_sound(self):
        
        sound = self.get_sounds(enums.AnimActions.TAKE_DAMAGE)[random.randint(0, len(self.get_sounds(enums.AnimActions.TAKE_DAMAGE))-1)]
        if not pygame.mixer.Channel(7).get_busy():
            pygame.mixer.Channel(7).play(sound)
        
    def take_damage(self, value: float, attacker=None, head_shot=False):
        
        if head_shot:
            if self.helmet_health > 0:
                self.helmet_health = math.clamp(self.helmet_health - value, 0, self.start_helmet_health)
                _popup_args = constants.POPUPS["damage"].copy()
                rand_sound = random.randint(0, len(self.get_sounds("helmet_bullet_sounds"))-1)
                self.get_sounds("helmet_bullet_sounds")[rand_sound].play()
                mc.popup(Popup(f'-0', self.pos + vec(self.rect.width / 2 - 20,-30) - self.player_offset, **_popup_args))
                if self.helmet_health == 0:
                    self.breaking_helmet = True
                    self.helmet_break_pos = vec(self.rect.topleft)
                    self.helmet_break_time = datetime.datetime.now()
                return False
        else:
            value *= self.body_damage_multiplier
        
        died = super().take_damage(value, attacker, head_shot)
        
        self.damage_sound()
        
        if died:
            self.get_sounds(enums.AnimActions.DEATH)[random.randint(0, len(self.get_sounds(enums.AnimActions.DEATH))-1)].play()
        
        return died