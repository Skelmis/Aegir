import ast


class Decor:
    def __init__(self, decor_name: str, _ast: ast.Call):
        self.decor_name: str = decor_name
        self._ast: ast.Call = _ast

    def __repr__(self):
        return f"<Decor(decor_name={self.decor_name})>"

    def as_v3(self) -> str:
        """Convert this decorator to its V3"""
        raise NotImplementedError

    @classmethod
    def from_ast(cls, _ast: ast.Call) -> "Decor":
        """
        Returns the relevant decorator or Decor if not known
        """
        from aegir.decorators import GuildOnly

        mappings = {"guild_only": GuildOnly}
        _func: ast.Attribute = _ast.func  # type: ignore
        func_name: str = _func.attr
        try:
            return mappings[func_name](func_name, _ast)
        except KeyError:
            return cls(func_name, _ast)
