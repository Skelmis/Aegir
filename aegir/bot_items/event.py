from copy import deepcopy
from typing import List

import libcst

from aegir import FormatError
from aegir.bot_items import Decorator
from aegir.util import EventParam, ActionType, DecoratorType


class Event:
    def __init__(
        self,
        name: str,
        cst: libcst.FunctionDef,
        *,
        decorators: List[Decorator],
        event_type: ActionType,
    ):
        self.name: str = name
        self.event_type: ActionType = event_type
        self.cst: libcst.FunctionDef = cst
        self.decorators: List[Decorator] = decorators

    def __repr__(self):
        return (
            f"{self.__class__.__name__}('{self.name}', has_errors={bool(self.errors)})"
        )

    @property
    def errors(self) -> List[FormatError]:
        errors: List[FormatError] = []
        for decor in self.decorators:
            if decor.decor_type == DecoratorType.EVENT and decor.was_called:
                fixed_cst = deepcopy(decor.cst)
                fixed_cst = fixed_cst.with_changes(decorator=fixed_cst.decorator.func)
                errors.append(
                    FormatError(
                        "Event's do not need to be called.", decor.cst, fixed_cst
                    )
                )

            elif decor.decor_type == DecoratorType.LISTENER and not decor.was_called:
                fixed_cst = deepcopy(decor.cst)
                fixed_cst = fixed_cst.with_changes(
                    decorator=libcst.Call(func=fixed_cst.decorator)
                )
                errors.append(
                    FormatError("Listener's must be called.", decor.cst, fixed_cst)
                )

        return errors
