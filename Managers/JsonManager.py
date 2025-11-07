import json

class JsonManager():
    
    def load_json(self, filepath):
        with open(filepath,'r') as file:
            return json.load(file)