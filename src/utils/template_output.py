import json
import os
from typing import Union

from src.utils import Configurable, ConfigKey
from .enums import TemplateMode


class TemplateOutput:

    @staticmethod
    def read(mode: TemplateMode) -> Union[list, dict]:
        path = os.path.join(TemplateMode.path.value, mode.value)
        with open(path, "r") as handle:
            return json.load(handle)

    @staticmethod
    def write(data: Union[list, dict], mode: TemplateMode, configurable: Configurable):
        path = os.path.join(configurable.path(ConfigKey.MASTER, 'samples_path'),
                            configurable.search(ConfigKey.MASTER, 'sample'),
                            mode.value)

        with open(path, "w") as handle:
            handle.write(json.dumps(data, indent=2))
