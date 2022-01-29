import ast
from typing import List

from aegir.decorators import Decor


class Command:
    def __init__(
        self,
        command_name: str,
        decorators: List[Decor],
        _ast: ast.AsyncFunctionDef,
    ):
        self.command_name: str = command_name
        self.decorators: List[Decor] = decorators

        self._ast: ast.AsyncFunctionDef = _ast

    def __repr__(self):
        return (
            f"<Command(command_name={self.command_name}, decorators={self.decorators})>"
        )

    @classmethod
    def from_ast(cls, _ast: ast.AsyncFunctionDef) -> "Command":
        decorators: List[Decor] = [
            Decor.from_ast(decor) for decor in _ast.decorator_list  # type: ignore
        ]

        return cls(_ast.name, decorators, _ast)
