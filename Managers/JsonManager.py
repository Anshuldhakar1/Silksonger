import json

class JsonManager():
    @staticmethod
    def load_json(filepath):
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_json(filepath, data):
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)