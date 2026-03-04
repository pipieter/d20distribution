__all__ = ("DiceParseError", "InvalidOperationError")

class DiceParseError(Exception):
    """Syntax error happened while parsing dice expression"""

    def __init__(self, msg: str) -> None: ...

class InvalidOperationError(Exception):
    """An invalid operation was found."""

    def __init__(self, msg: str) -> None: ...
