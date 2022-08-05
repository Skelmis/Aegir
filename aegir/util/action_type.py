from enum import Enum
from typing import NamedTuple, List, Dict

import libcst


class EventParam(NamedTuple):
    args: List
    kwargs: Dict
    cst: libcst.Parameters


class ActionType(Enum):
    EVENT = 1
    LISTENER = 2
    UNKNOWN = 3
    COMMAND = 4
