import json


class Configurable:

    def __init__(self, config_file_path):
        with open(config_file_path, "r") as json_file:
            self.config = json.load(json_file)
