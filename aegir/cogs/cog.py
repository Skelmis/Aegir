import ast
from typing import List

from aegir.cogs.cog_listener import CogListener
from aegir.cogs.cog_command import CogCommand


class Cog:
    def __init__(
        self,
        _ast: ast.ClassDef,
        has_imported_nextcord: bool = False,
        has_imported_nextcord_commands: bool = False,
    ):
        self._ast: ast.ClassDef = _ast

        self.has_imported_nextcord: bool = has_imported_nextcord
        self.has_imported_nextcord_commands: bool = has_imported_nextcord_commands

        self._commands: List[CogCommand] = []
        self._listeners: List[CogListener] = []
