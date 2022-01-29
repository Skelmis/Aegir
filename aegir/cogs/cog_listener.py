import ast


class CogListener:
    def __init__(self, _ast: ast.AsyncFunctionDef):
        self._ast: ast.AsyncFunctionDef = _ast
