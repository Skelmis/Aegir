class FormatError:
    def __init__(self, message: str, old_cst, fixed_cst):
        self.message: str = message
        self.old_cst = old_cst
        self.fixed_cst = fixed_cst

    def __repr__(self):
        return f"FormatError('{self.message}')"
