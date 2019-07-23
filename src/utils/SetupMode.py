from enum import Enum, unique


@unique
class SetupMode(Enum):
    NEW = 0
    OLD = 1
