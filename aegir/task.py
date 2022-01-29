import ast


class Task:
    def __init__(
        self,
        task_name: str,
        _ast: ast.AsyncFunctionDef,
    ):
        self.task_name: str = task_name
        self._ast: ast.AsyncFunctionDef = _ast

    def __repr__(self):
        return f"<Task(task_name={self.task_name})>"

    @classmethod
    def from_ast(cls, _ast: ast.AsyncFunctionDef) -> "Task":
        return cls(_ast.name, _ast)
