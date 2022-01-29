import ast
from pathlib import Path
from typing import List, Union

from aegir.cogs.cog import Cog
from aegir.command import Command
from aegir.event import Event
from aegir.exceptions import InvalidDirPath


class Aegir:
    def __init__(self, dir_path: str):
        self._dir_path: Path = Path(dir_path).absolute()

        self.has_imported_nextcord: bool = False
        self.has_imported_nextcord_commands: bool = False
        self._cogs: List[Cog] = []
        self._instance_name: str = ""
        self._main_file: List[Event, Command] = []

        if not self._dir_path.exists():
            raise InvalidDirPath

    def __repr__(self):
        return (
            f"<Aegir, instance_name={self._instance_name}, "
            f"has_imported_nextcord={self.has_imported_nextcord}, "
            f"has_imported_nextcord_commands={self.has_imported_nextcord_commands}, "
            f"main_file={self._main_file}, cogs={self._cogs}>"
        )

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

    def as_command_or_event(self, _ast: ast.AsyncFunctionDef) -> Union[Command, Event]:
        for i, decor in enumerate(_ast.decorator_list):
            func_name = self.as_attr_or_name(decor.func)  # type: ignore
            if func_name == "event":
                _ast.decorator_list.pop(i)
                return Event.from_ast(_ast)
            elif func_name == "command":
                _ast.decorator_list.pop(i)
                return Command.from_ast(_ast)

        raise NotImplementedError

    @staticmethod
    def resolve_imported(_ast: Union[ast.Import, ast.ImportFrom]) -> str:
        """Given an ast, return the thing imported"""
        return _ast.names[0].name

    def parse_ast(self, _ast):
        if isinstance(_ast, (ast.Import, ast.ImportFrom)):
            imported = self.resolve_imported(_ast)
            if imported == "nextcord":
                self.has_imported_nextcord = True

            elif imported == "commands":
                self.has_imported_nextcord_commands = True

        elif isinstance(_ast, ast.If):
            # __name__ == "__main__"
            for _new_ast in _ast.body:
                self.parse_ast(_new_ast)

        elif isinstance(_ast, ast.Assign):
            var_name = _ast.targets[0].id
            value_func = _ast.value.func
            value = self.as_attr_or_name(value_func)

            if value in {"Bot", "Client"}:
                self._instance_name = var_name

        elif isinstance(_ast, ast.AsyncFunctionDef):
            event_or_command = self.as_command_or_event(_ast)
            self._main_file.append(event_or_command)

    def convert(self):
        for file in self._dir_path.glob("**/*.py"):
            ast_module = self.as_ast(file)
            for _ast in ast_module.body:
                self.parse_ast(_ast)

        print(repr(self))
