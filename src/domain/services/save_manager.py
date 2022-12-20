import os, pickle

class SaveManager:
    def __init__ (self, file_extension: str, save_folder: str):
        self.file_extension = file_extension
        self.save_folder = save_folder
        
    def save_data(self, data, name):
        data_file = open(self.save_folder+name+self.file_extension,  "wb")
    
        pickle.dump(data, data_file)
        
    def load_data(self, name):
        data_file = open(self.save_folder+name+self.file_extension,"rb")
        data = pickle.load(data_file)
        return data
    
    def check_for_file(self, name) :
        return os.path.exists(self.save_folder+name+self.file_extension)
    
    def load_game_data(self, file_names: list[str], defaults: list[object]):
        values = []
        for i, file in enumerate(file_names):
            if self.check_for_file(file):
                values.append(self.load_data(file))
            else:
                values.append(defaults[i])
        
        if len(values) > 1:
            return tuple(values)
        return values[0]
    
    def save_game_data(self, data: list[object], file_names: list[str]):
        for i, file in enumerate(data):
            self.save_data(file, file_names[i])