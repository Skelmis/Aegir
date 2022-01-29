import ast
from typing import Optional


class TaskBeforeAfter:
    def __init__(self, associated_task: str, _ast: ast.AsyncFunctionDef):
        self.associated_task: str = associated_task
        self._ast: ast.AsyncFunctionDef = _ast

    def __repr__(self):
        return f"<{self.__class__.__name__}(associated_task={self.associated_task})>"

    @classmethod
    def from_ast(
        cls, _ast: ast.AsyncFunctionDef, decor: ast.Attribute
    ) -> "TaskBeforeAfter":
        associated_task = decor.value.id
        return cls(associated_task, _ast)


class BeforeLoop(TaskBeforeAfter):
    pass


class AfterLoop(TaskBeforeAfter):
    pass


class Task:
    def __init__(
        self,
        task_name: str,
        _ast: ast.AsyncFunctionDef,
    ):
        self.task_name: str = task_name

        self.before_loop: Optional[BeforeLoop] = None
        self.after_loop: Optional[AfterLoop] = None

        self._ast: ast.AsyncFunctionDef = _ast

    def __repr__(self):
        return (
            f"<Task(task_name={self.task_name}, "
            f"before_loop={self.before_loop}, "
            f"after_loop={self.after_loop})>"
        )

    @classmethod
    def from_ast(cls, _ast: ast.AsyncFunctionDef) -> "Task":
        return cls(_ast.name, _ast)
