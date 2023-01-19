import os, pickle

from domain.utils import enums
from domain.services import resources, game_controller

class AssetsManager:
    def __init__ (self, enemy_types: list[enums.Enemies]):
        self.enemy_types = enemy_types
        
        #region z_roger
        self.z_roger_damage_sounds, self.z_roger_death_sounds, self.z_roger_attack_sounds = None, None, None
        self.z_roger_run_frames, self.z_roger_attack_frames, self.z_roger_death_frames = None, None, None
        #endregion
        
        #region z_ronaldo
        self.z_ronaldo_damage_sounds, self.z_ronaldo_death_sounds, self.z_ronaldo_attack_sounds = None, None, None
        self.z_ronaldo_run_frames, self.z_ronaldo_attack_frames, self.z_ronaldo_death_frames = None, None, None
        #endregion
        
        #region z_robert
        self.z_robert_damage_sounds, self.z_robert_death_sounds, self.z_robert_attack_sounds = None, None, None
        self.z_robert_run_frames, self.z_robert_attack_frames, self.z_robert_death_frames = None, None, None
        #endregion
        
        #region z_rui
        self.z_rui_damage_sounds, self.z_rui_death_sounds, self.z_rui_attack_sounds, self.z_rui_bump_sounds = None, None, None, None
        self.z_rui_run_frames, self.z_rui_attack_frames1, self.z_rui_attack_frames2, self.z_rui_death_frames = None, None, None, None
        #endregion
        
        #region z_raven
        self.z_raven_damage_sounds, self.z_raven_death_sounds, self.z_raven_attack_sounds, self.z_raven_dash_sounds = None, None, None, None
        self.z_raven_run_frames, self.z_raven_attack_frames, self.z_raven_death_frames = None, None, None
        #endregion
        
        #region z_raimundo
        self.z_raimundo_run_frames_1, self.z_raimundo_run_frames_2, self.z_raimundo_run_frames_3, self.z_raimundo_run_frames_4 = None, None, None, None
        self.z_raimundo_attack_frames1, self.z_raimundo_attack_frames2, self.z_raimundo_attack_frames3, self.z_raimundo_attack_frames4 = None, None, None, None
        self.z_raimundo_death_frames1, self.z_raimundo_death_frames2, self.z_raimundo_death_frames3, self.z_raimundo_death_frames4 = None, None, None, None
        self.z_raimundo_helmet_frames = None
        self.z_raimundo_damage_sounds, self.z_raimundo_death_sounds, self.z_raimundo_attack_sounds, self.z_raimundo_helmet_bullet_sounds = None, None, None, None
        #endregion
        
        #region z_roger
        self.z_ronald_damage_sounds, self.z_ronald_death_sounds, self.z_ronald_attack_sounds = None, None, None
        self.z_ronald_run_frames, self.z_ronald_attack_frames, self.z_ronald_death_frames = None, None, None
        #endregion
        
    
    def get_assets(self, enemy_type: enums.Enemies, attr_name: str):
        return getattr(self, f'{enemy_type.value}_{attr_name}')
        
    
    def load_resources(self):
        for t in self.enemy_types:
            match t:
                case enums.Enemies.Z_ROGER:
                    self.load_roger()
                case enums.Enemies.Z_RONALDO:
                    self.load_ronaldo()
                case enums.Enemies.Z_ROBERT:
                    self.load_robert()
                case enums.Enemies.Z_RUI:
                    self.load_rui()
                case enums.Enemies.Z_RAIMUNDO:
                    self.load_raimundo()
                case enums.Enemies.Z_RAVEN:
                    self.load_raven()
                case enums.Enemies.Z_RONALD:
                    self.load_ronald()
        
        
    
    def load_roger(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_ROGER, enums.AnimActions.RUN)
        self.z_roger_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_ROGER, enums.AnimActions.ATTACK)
        self.z_roger_attack_frames = game_controller.load_sprites(attack_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_ROGER, enums.AnimActions.DEATH)
        self.z_roger_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_roger_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROGER, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_roger_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROGER, enums.AnimActions.DEATH), 0.2)
        self.z_roger_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROGER, enums.AnimActions.ATTACK), 0.2)

        
    def load_ronaldo(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_RONALDO, enums.AnimActions.RUN)
        self.z_ronaldo_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_RONALDO, enums.AnimActions.ATTACK)
        self.z_ronaldo_attack_frames = game_controller.load_sprites(attack_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_RONALDO, enums.AnimActions.DEATH)
        self.z_ronaldo_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_ronaldo_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_ronaldo_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.DEATH), 0.2)
        self.z_ronaldo_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALDO, enums.AnimActions.ATTACK), 0.2)
        
        
    def load_robert(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_ROBERT, enums.AnimActions.RUN)
        self.z_robert_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_ROBERT, enums.AnimActions.ATTACK)
        self.z_robert_attack_frames = game_controller.load_sprites(attack_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_ROBERT, enums.AnimActions.DEATH)
        self.z_robert_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_robert_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROBERT, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_robert_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROBERT, enums.AnimActions.DEATH), 0.2)
        self.z_robert_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_ROBERT, enums.AnimActions.ATTACK), 0.2)
        
        
    def load_rui(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_RUI, enums.AnimActions.RUN)
        self.z_rui_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_RUI, enums.AnimActions.ATTACK)
        self.z_rui_attack_frames1 = game_controller.load_sprites(attack_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_rui_attack_frames2 = game_controller.load_sprites(attack_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_RUI, enums.AnimActions.DEATH)
        self.z_rui_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_rui_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RUI, enums.AnimActions.TAKE_DAMAGE), 0.4)
        self.z_rui_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RUI, enums.AnimActions.DEATH).replace("01.mp3",""), 0.4)
        self.z_rui_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RUI, enums.AnimActions.ATTACK), 0.4)
        self.z_rui_bump_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RUI, enums.AnimActions.BUMP), 0.5)
        
        
    def load_raven(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_RAVEN, enums.AnimActions.RUN)
        self.z_raven_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_RAVEN, enums.AnimActions.ATTACK)
        self.z_raven_attack_frames = game_controller.load_sprites(attack_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_RAVEN, enums.AnimActions.DEATH)
        self.z_raven_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_raven_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAVEN, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_raven_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAVEN, enums.AnimActions.DEATH), 0.8)
        self.z_raven_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAVEN, enums.AnimActions.ATTACK), 0.2)
        self.z_raven_dash_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAVEN, enums.AnimActions.DASH), 0.1)
        
        
    def load_raimundo(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.RUN)
        self.z_raimundo_run_frames_1 = game_controller.load_sprites(run_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_run_frames_2 = game_controller.load_sprites(run_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_run_frames_3 = game_controller.load_sprites(run_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_run_frames_4 = game_controller.load_sprites(run_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.ATTACK)
        self.z_raimundo_attack_frames1 = game_controller.load_sprites(attack_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_attack_frames2 = game_controller.load_sprites(attack_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_attack_frames3 = game_controller.load_sprites(attack_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_attack_frames4 = game_controller.load_sprites(attack_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.DEATH)
        self.z_raimundo_death_frames1 = game_controller.load_sprites(death_folder + "\\01", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_death_frames2 = game_controller.load_sprites(death_folder + "\\02", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_death_frames3 = game_controller.load_sprites(death_folder + "\\03", convert_type=enums.ConvertType.CONVERT_ALPHA)
        self.z_raimundo_death_frames4 = game_controller.load_sprites(death_folder + "\\04", convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_raimundo_helmet_frames = game_controller.load_sprites(f'{resources.IMAGES_PATH}enemies\\{str(enums.Enemies.Z_RAIMUNDO.value)}\\helmet_breaking\\', convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_raimundo_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_raimundo_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.DEATH), 0.2)
        self.z_raimundo_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RAIMUNDO, enums.AnimActions.ATTACK), 0.2)
        self.z_raimundo_helmet_bullet_sounds = game_controller.load_sounds(f'{resources.SOUNDS_PATH}sound_effects\\enemies\\{str(enums.Enemies.Z_RAIMUNDO.value)}\\helmet_bullet_hit\\', 0.2)
        
    def load_ronald(self):
        run_folder = resources.get_enemy_path(enums.Enemies.Z_RONALD, enums.AnimActions.RUN)
        self.z_ronald_run_frames = game_controller.load_sprites(run_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        attack_folder = resources.get_enemy_path(enums.Enemies.Z_RONALD, enums.AnimActions.ATTACK)
        self.z_ronald_attack_frames = game_controller.load_sprites(attack_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        death_folder = resources.get_enemy_path(enums.Enemies.Z_RONALD, enums.AnimActions.DEATH)
        self.z_ronald_death_frames = game_controller.load_sprites(death_folder, convert_type=enums.ConvertType.CONVERT_ALPHA)
        
        self.z_ronald_damage_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALD, enums.AnimActions.TAKE_DAMAGE), 0.1)
        self.z_ronald_death_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALD, enums.AnimActions.DEATH), 0.2)
        self.z_ronald_attack_sounds = game_controller.load_sounds(resources.get_enemy_sfx(enums.Enemies.Z_RONALD, enums.AnimActions.ATTACK), 0.2)




