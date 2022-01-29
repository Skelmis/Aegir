import ast
from pathlib import Path


class Aegir:
    def __init__(self, dir_path: str):
        self._dir_path: Path = Path(dir_path).absolute()

        if not self._dir_path.exists():
            raise

    @staticmethod
    def as_ast(file_path: Path) -> ast.Module:
        """Parse a given file"""
        source = file_path.read_text()
        tree = ast.parse(source)
        return tree

    def parse_ast(self, _ast: ast.Module):
        pass

    def convert(self):
        for file in self._dir_path.glob("**/*.py"):
            ast_module = self.as_ast(file)
            self.parse_ast(ast_module)
