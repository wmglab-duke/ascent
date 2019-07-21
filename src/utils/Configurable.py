import json


class Configurable:

    def __init__(self, config_file_path: str):

        if not config_file_path[-5:] == '.json':
            raise Exception('\n\tcode:\t-1\n'
                            '\ttext:\tConfiguration file path must end in .json\n'
                            '\tsource:\tConfigurable.py')

        with open(config_file_path, "r") as json_file:
            self.config: dict = json.load(json_file)
