from enum import Enum, unique


@unique
class ConfigKey(Enum):
    MASTER = 'master'
    EXCEPTIONS = 'exceptions'
