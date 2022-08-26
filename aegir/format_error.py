class FormatError:
    def __init__(self, *, title: str, description: str, old_cst, fixed_cst):
        self.title: str = title
        self.description: str = description
        self.old_cst = old_cst
        self.fixed_cst = fixed_cst

    def __repr__(self):
        return f"FormatError(title='{self.title}')"

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "old_cst": self.old_cst,
            "fixed_cst": self.fixed_cst,
        }
