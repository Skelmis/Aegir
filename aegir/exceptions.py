class AegirException(Exception):
    """A base exception class."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message


class InvalidDirPath(AegirException):
    """The given starting path does not exist."""
