import libcst

from aegir.util import DecoratorType


class Decorator:
    def __init__(self, name: str, decor_type: DecoratorType, cst: libcst.Decorator):
        self.name: str = name
        self.decor_type: DecoratorType = decor_type
        self.cst: libcst.Decorator = cst

    def __repr__(self):
        return f"Decorator(name='{self.name}')"

    @property
    def was_called(self) -> bool:
        """Returns True if this decorator was called."""
        return isinstance(self.cst.decorator, libcst.Call)
