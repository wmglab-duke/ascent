import json
import os
from typing import Union

from src.utils import Configurable, Config
from .enums import TemplateMode


class TemplateOutput:

    @staticmethod
    def read(mode: TemplateMode) -> Union[list, dict]:
        path = os.path.join(TemplateMode.path.value, mode.value)
        with open(path, "r") as handle:
            return json.load(handle)

    @staticmethod
    def write(data: Union[list, dict], mode: TemplateMode, configurable: Configurable):
        path = os.path.join(configurable.path(Config.SAMPLE, 'samples_path'),
                            str(configurable.search(Config.RUN, 'sample')),
                            mode.value)
        print(path)

        with open(path, "w") as handle:
            handle.write(json.dumps(data, indent=2))
