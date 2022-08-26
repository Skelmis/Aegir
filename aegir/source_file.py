from __future__ import annotations

import logging
from typing import Union, cast, Optional, Type, TYPE_CHECKING

import libcst

from aegir import ParsedData
from aegir.bot_items import Event, Listener, Command, Decorator
from aegir.util import RunMode, ImportFrom, Import, ActionType, DecoratorType

if TYPE_CHECKING:
    from aegir import Aegir

log = logging.getLogger(__name__)


class SourceFile:
    """Parse a piece of standalone code."""

    def __init__(
        self,
        source: str,
        *,
        backref: Union[Aegir, Type[Aegir]],
        bot_variable: Optional[str] = None,
    ):
        self._source: str = source
        self.commands: list[Command] = []
        self.__entry_func: Optional[str] = None
        self.__run_mode: RunMode = RunMode.unknown
        self.file_cst: Optional[libcst.Module] = None
        self.events: list[Union[Event, Listener]] = []
        self._bot_variable: str = bot_variable or ""
        self._backref: Union[Aegir, Type[Aegir]] = backref
        self.__imports: list[Union[Import, ImportFrom]] = []

    def convert(self) -> ParsedData:
        self.file_cst = self._backref.as_cst(self._source)
        if self.__run_mode == RunMode.unknown:
            self.__run_mode = RunMode.bot_run

        where_are_things_defined: list = self.file_cst.body  # type: ignore
        if self.__run_mode == RunMode.asyncio_run:
            # We need to find that function it runs
            # because everything will be defined there
            break_loop = False
            for item in where_are_things_defined:
                if break_loop:
                    break

                if not isinstance(item, libcst.FunctionDef):
                    continue

                if item.name.value == self.__entry_func:
                    # FunctionDef.body->IndentedBlock.body->List[Lines]
                    where_are_things_defined.extend(item.body.body)
                    break_loop = True

        # print(where_are_things_defined)
        for nest in where_are_things_defined:
            if isinstance(nest, libcst.SimpleStatementLine):
                # nest here is a simple statement line, a wrapper for each newline
                item = nest.body[0]
                if isinstance(item, libcst.Import):
                    self.__imports.append(self._backref.parse_out_import(item))

                elif isinstance(item, libcst.ImportFrom):
                    self.__imports.append(self._backref.parse_out_import_from(item))

            elif isinstance(nest, libcst.If):
                # Likely a if __name__ == "__main__":
                # and is thus hard coded for this standard
                compare_body = nest.test
                compare_body = cast(libcst.Comparison, compare_body)
                left_compare = compare_body.left.value  # type: ignore
                right_compare = compare_body.comparisons[0].comparator.value  # type: ignore
                assert isinstance(
                    compare_body.comparisons[0].operator,
                    libcst.Equal,
                ), "Expected == comparison for entrypoint"
                assert (
                    left_compare == "__name__" and right_compare == '"__main__"'
                ) or (
                    left_compare == '"__main__"' and right_compare == "__name__"
                ), "Expected entrypoint __main__ comparison"
                self.parse_run_mode(nest.body.body)  # type: ignore

            elif isinstance(nest, libcst.FunctionDef):
                action: Union[
                    Command, Event, Listener, None
                ] = self.parse_for_possible_event_or_command(nest)
                if isinstance(action, Command):
                    self.commands.append(action)
                elif isinstance(action, (Event, Listener)):
                    self.events.append(action)

        errors = []
        for event in self.events:
            errors.extend(event.errors)

        for command in self.commands:
            errors.extend(command.errors)

        return ParsedData(errors=errors, commands=self.commands, events=self.events)

    def parse_for_possible_event_or_command(
        self, cst: libcst.FunctionDef
    ) -> Union[Command, Event, None]:
        # sanity check before we get too deep
        if not isinstance(cst.asynchronous, libcst.Asynchronous):
            return

        function_name: str = cst.name.value
        if function_name == self.__entry_func:
            return

        action_type: ActionType = ActionType.UNKNOWN
        decorators: list[Decorator] = []
        cst_decorators: List[libcst.Decorator] = cst.decorators  # type: ignore
        for cst_decor in cst_decorators:
            decor_name = self._backref.recursive_attribute_resolution(
                cst_decor.decorator, ""
            )
            if (
                decor_name.startswith(self._bot_variable)
                or decor_name.startswith("bot")
                or decor_name.startswith("client")
            ):
                if decor_name.endswith(".event"):
                    decorators.append(
                        Decorator(decor_name, DecoratorType.EVENT, cst_decor)
                    )
                    action_type = ActionType.EVENT
                elif decor_name.endswith(".command"):
                    decorators.append(
                        Decorator(decor_name, DecoratorType.COMMAND, cst_decor)
                    )
                    action_type = ActionType.COMMAND
                elif decor_name.endswith(".listen"):
                    decorators.append(
                        Decorator(decor_name, DecoratorType.LISTENER, cst_decor)
                    )
                    action_type = ActionType.LISTENER

            # Checks
            elif decor_name.startswith("commands.") or decor_name.startswith(
                "application_checks."
            ):
                Decorator(decor_name, DecoratorType.CHECK, cst_decor)

            else:
                decorators.append(
                    Decorator(decor_name, DecoratorType.UNKNOWN, cst_decor)
                )

        if action_type == ActionType.UNKNOWN:
            log.warning(
                "Couldn't figure out what type of action '%s' was", function_name
            )

        elif action_type == ActionType.EVENT:
            return Event(
                function_name,
                decorators=decorators,
                event_type=action_type,
                cst=cst,
            )

        elif action_type == ActionType.LISTENER:
            return Listener(
                function_name,
                decorators=decorators,
                event_type=action_type,
                cst=cst,
            )

    def parse_run_mode(self, possible_csts: list[libcst.SimpleStatementLine]) -> None:
        for line in possible_csts:
            try:
                line_doing = line.body[0].value  # type: ignore
            except (AttributeError, TypeError):
                continue

            if isinstance(line_doing, libcst.Await):
                line_doing = line_doing.expression

            if not isinstance(line_doing, libcst.Call):
                # Skip lines not calling something
                continue

            func_call = self._backref.recursive_attribute_resolution(
                line_doing.func, ""  # type: ignore
            )
            if func_call == "asyncio.run":
                call_arguments: List[libcst.Arg] = line_doing.args  # type: ignore
                assert len(call_arguments) == 1, "asyncio.run only takes one argument"
                self.__run_mode = RunMode.asyncio_run
                self.__entry_func = call_arguments[0].value.func.value  # type: ignore
                return

            elif func_call in (
                f"{self._bot_variable}.run",
                f"{self._bot_variable}.start",
                "bot.start",
                "bot.run",
                "client.start",
                "client.run",
            ):
                call_arguments: List[libcst.Arg] = line_doing.args  # type: ignore
                assert (
                    len(call_arguments) == 1
                ), f"{func_call} takes one argument which should be the token"
                self.__run_mode = RunMode.bot_run
                return
