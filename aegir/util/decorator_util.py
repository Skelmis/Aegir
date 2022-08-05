from enum import Enum


class DecoratorType(Enum):
    EVENT = 1
    LISTENER = 2
    CHECK = 3
    UNKNOWN = 4
    COMMAND = 5
