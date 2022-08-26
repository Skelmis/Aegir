import logging
from copy import deepcopy
from typing import List, Union, cast

import libcst

from aegir import FormatError
from aegir.bot_items import Decorator
from aegir.util import EventParam, ActionType, DecoratorType

log = logging.getLogger(__name__)


class Event:
    def __init__(
        self,
        name: str,
        cst: libcst.FunctionDef,
        *,
        decorators: List[Decorator],
        event_type: ActionType,
        is_in_cog: bool = False,
    ):
        self.name: str = name
        self.is_in_cog: bool = is_in_cog
        self.cst: libcst.FunctionDef = cst
        self.event_type: ActionType = event_type
        self.decorators: List[Decorator] = decorators

    def _get_named_arguments(self) -> list[str]:
        """Return a list of the names of arguments."""
        args = []
        for param in self.cst.params.params:
            args.append(param.name.value)
        return args

    def _guess_bot_variable(self) -> str:
        return self.decorators[0].name.split(".")[0]

    def __repr__(self):
        return (
            f"{self.__class__.__name__}('{self.name}', has_errors={bool(self.errors)})"
        )

    @property
    def does_function_processes_commands(self) -> bool:
        result = any(
            self._parse_body_for_process_commands(b) for b in self.cst.body.body
        )
        return result

    def _parse_body_for_process_commands(self, cst) -> bool:
        if isinstance(cst, libcst.If):
            if not isinstance(cst.body, libcst.IndentedBlock):
                return False

            indented_cst = cst.body.body
            if not isinstance(indented_cst, list):
                raise ValueError(indented_cst)

            return any(self._parse_body_for_process_commands(i) for i in indented_cst)

        elif isinstance(cst, list):
            return any(self._parse_body_for_process_commands(i) for i in cst)

        elif isinstance(cst, libcst.SimpleStatementLine) and isinstance(
            cst.body[0], libcst.Expr
        ):
            cst: libcst.BaseSmallStatement = cst.body[0]
            cst: libcst.Expr = cast(libcst.Expr, cst)
            child = cst.children[0] if cst.children else None
            if not isinstance(child, libcst.Await):
                return False

            if not isinstance(child.expression, libcst.Call):
                return False

            expression: libcst.Call = child.expression
            bot_name = expression.func.value
            if isinstance(bot_name, libcst.Attribute):
                bot_name = bot_name.attr

            if isinstance(bot_name, libcst.Name):
                bot_name = bot_name.value

            method = expression.func.attr
            if isinstance(method, libcst.Name):
                method = method.value

            if method == "process_commands":
                if bot_name not in ("bot", "client"):
                    log.debug(
                        "Guessing they process commands as they dont use bot or client as a variable name. %s",
                        expression.func,
                    )

                return True

        return False

    @property
    def errors(self) -> List[FormatError]:
        errors: List[FormatError] = []
        for decor in self.decorators:
            if decor.decor_type == DecoratorType.EVENT and decor.was_called:
                fixed_cst = deepcopy(decor.cst)
                fixed_cst = fixed_cst.with_changes(decorator=fixed_cst.decorator.func)
                errors.append(
                    FormatError(
                        title="Event's do not need to be called.",
                        description="When defining an event on your bot variable you do not need to use brackets.",
                        old_cst=decor.cst,
                        fixed_cst=fixed_cst,
                    )
                )

            elif decor.decor_type == DecoratorType.LISTENER and not decor.was_called:
                fixed_cst = deepcopy(decor.cst)
                fixed_cst = fixed_cst.with_changes(
                    decorator=libcst.Call(func=fixed_cst.decorator)
                )
                errors.append(
                    FormatError(
                        title="Listener's must be called.",
                        description="When defining a listener on your bot variable you do need to use brackets.",
                        old_cst=decor.cst,
                        fixed_cst=fixed_cst,
                    )
                )

        # Do actions for entire event
        if (
            self.event_type == ActionType.EVENT
            and self.name == "on_message"
            and not self.does_function_processes_commands
        ):
            fixed_cst = deepcopy(self.cst)
            args = self._get_named_arguments()
            fix = libcst.SimpleStatementLine(
                [
                    libcst.Expr(
                        libcst.Await(
                            libcst.Call(
                                libcst.Attribute(
                                    libcst.Name(self._guess_bot_variable()),
                                    libcst.Name("process_commands"),
                                ),
                                args=[
                                    libcst.Arg(
                                        libcst.Name(
                                            args[1] if self.is_in_cog else args[0]
                                        )
                                    )
                                ],
                            )
                        )
                    )
                ]
            )
            body = list(fixed_cst.body.body)
            body.append(fix)
            body = fixed_cst.body.with_changes(body=body)
            fixed_cst = fixed_cst.with_changes(body=body)
            errors.append(
                FormatError(
                    title="Overriding on_message without process_commands.",
                    description="Looks like you override the on_message event "
                    "without processing commands.\n This means your commands "
                    "will not get called at all, you should change your event to the below.\n\n"
                    "Note: This may not be in the right place so double check it is.\n\n"
                    f"You can read more about it at https://docs.disnake.dev/en/latest/faq.html"
                    "?highlight=frequently#why-does-on-message-make-my-commands-stop-working",
                    old_cst=self.cst,
                    fixed_cst=fixed_cst,
                )
            )

        return errors
