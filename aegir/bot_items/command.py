from aegir import FormatError


class Command:
    def __init__(self, name: str):
        self.name: str = name

    def add_extra_decor(
        self,
    ):
        ...

    @property
    def errors(self) -> list[FormatError]:
        return []
