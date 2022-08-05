class Command:
    def __init__(self, name: str):
        self.name: str = name

    def add_extra_decor(
        self,
    ):
        ...
