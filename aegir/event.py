import ast


class Event:
    def __init__(
        self,
        event_name: str,
        _ast: ast.AsyncFunctionDef,
    ):
        self.event_name: str = event_name
        self._ast: ast.AsyncFunctionDef = _ast

    def __repr__(self):
        return f"<Event(event_name={self.event_name})>"

    @classmethod
    def from_ast(cls, _ast: ast.AsyncFunctionDef) -> "Event":
        return cls(_ast.name, _ast)
