import ast
from pathlib import Path
from typing import List, Union, Set, Dict

from aegir.cogs.cog import Cog
from aegir.command import Command
from aegir.event import Event
from aegir.exceptions import InvalidDirPath, PlainAsyncFunc
from aegir.task import Task, BeforeLoop, AfterLoop


class Aegir:
    def __init__(self, dir_path: str, subclass_name: str = ""):
        """
        Parameters
        ----------
        dir_path
        subclass_name: str
            What your bot subclass is called
        """
        self._dir_path: Path = Path(dir_path).absolute()

        self.has_imported_nextcord: bool = False
        self.has_imported_nextcord_commands: bool = False
        self._cogs: List[Cog] = []
        self._instance_name: str = ""
        self._main_file: List[Event, Command, Task] = []
        self._task_hooks: Dict[str, List[Union[BeforeLoop, AfterLoop]]] = {}

        self._possible_bot_classes: Set = {"Bot", "Client"}
        if subclass_name:
            self._possible_bot_classes.add(subclass_name)

        if not self._dir_path.exists():
            raise InvalidDirPath

        self.has_been_converted: bool = False

    def __repr__(self):
        return (
            f"<Aegir, instance_name={self._instance_name}, "
            f"has_imported_nextcord={self.has_imported_nextcord}, "
            f"has_imported_nextcord_commands={self.has_imported_nextcord_commands}, "
            f"main_file={self._main_file}, cogs={self._cogs}>"
        )

    @property
    def events(self) -> List[Event]:
        return [i for i in self._main_file if isinstance(i, Event)]

    @property
    def commands(self) -> List[Command]:
        return [i for i in self._main_file if isinstance(i, Command)]

    @property
    def tasks(self) -> List[Task]:
        return [i for i in self._main_file if isinstance(i, Task)]

    @staticmethod
    def as_ast(file_path: Path) -> ast.Module:
        """Parse a given file"""
        source = file_path.read_text()
        tree = ast.parse(source)
        return tree

    @staticmethod
    def as_attr_or_name(_ast: Union[ast.Attribute, ast.Name]) -> str:
        if isinstance(_ast, ast.Name):
            return _ast.id
        elif isinstance(_ast, ast.Attribute):
            return _ast.attr

        raise NotImplementedError

    def as_command_or_event(
        self, _ast: ast.AsyncFunctionDef
    ) -> Union[Command, Event, Task, BeforeLoop, AfterLoop]:
        if not _ast.decorator_list:
            raise PlainAsyncFunc

        for i, decor in enumerate(_ast.decorator_list):
            if isinstance(decor, ast.Attribute):
                func_name = self.as_attr_or_name(decor)
            else:
                func_name = self.as_attr_or_name(decor.func)  # type: ignore

            if func_name == "event":
                obj = Event
            elif func_name == "command":
                obj = Command
            elif func_name == "loop":
                obj = Task
            elif func_name == "before_loop":
                return BeforeLoop.from_ast(_ast, decor)
            elif func_name == "after_loop":
                return AfterLoop.from_ast(_ast, decor)
            # TODO Handle both command error and task error
            else:
                continue

            _ast.decorator_list.pop(i)
            return obj.from_ast(_ast)

            # TODO before_invoke, after_invoke

        raise NotImplementedError

    @staticmethod
    def resolve_imported(_ast: Union[ast.Import, ast.ImportFrom]) -> str:
        """Given an ast, return the thing imported"""
        return _ast.names[0].name

    def parse_ast(self, _ast):
        if hasattr(_ast, "__iter__"):
            for new_ast in _ast:
                self.parse_ast(new_ast)

        if isinstance(_ast, (ast.Import, ast.ImportFrom)):
            imported = self.resolve_imported(_ast)
            if imported == "nextcord":
                self.has_imported_nextcord = True

            elif imported == "commands":
                self.has_imported_nextcord_commands = True

        elif isinstance(_ast, ast.If):
            # __name__ == "__main__"
            self.parse_ast(_ast.body)

        elif isinstance(_ast, ast.Assign):
            var_name = self.as_attr_or_name(_ast.targets[0])  # type: ignore
            if not isinstance(_ast.value, ast.Call):
                # Don't need constants n such
                return

            value_func = _ast.value.func

            value = self.as_attr_or_name(value_func)  # type: ignore

            if value in self._possible_bot_classes:
                self._instance_name = var_name

        elif isinstance(_ast, ast.AsyncFunctionDef):
            try:
                event_or_command = self.as_command_or_event(_ast)
            except PlainAsyncFunc:
                # async def main():
                self.parse_ast(_ast.body)
                return
            except NotImplementedError:
                return

            if isinstance(event_or_command, (BeforeLoop, AfterLoop)):
                try:
                    self._task_hooks[event_or_command.associated_task].append(
                        event_or_command
                    )
                except KeyError:
                    self._task_hooks[event_or_command.associated_task] = [
                        event_or_command
                    ]
            else:
                self._main_file.append(event_or_command)

    def hook_tasks(self):
        """Takes BeforeLoop's and AfterLoop's and
        hooks them into the relevant tasks.
        """
        for item in self._main_file:
            if not isinstance(item, Task):
                continue

            task_name = item.task_name
            try:
                loops = self._task_hooks[task_name]
            except KeyError:
                continue

            assert len(loops) in {0, 1, 2}

            for invoke in loops:
                if isinstance(invoke, BeforeLoop):
                    item.before_loop = invoke
                else:
                    item.after_loop = invoke

    def convert(self):
        for file in self._dir_path.glob("**/*.py"):
            ast_module = self.as_ast(file)
            for _ast in ast_module.body:
                self.parse_ast(_ast)

        self.hook_tasks()
        self.has_been_converted = True

        print(repr(self))
