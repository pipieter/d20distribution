__all__ = ("DiceParseError",)


class DiceParseError(Exception):
    """Syntax error happened while parsing dice expression"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class InvalidOperationError(Exception):
    """An invalid operation was found."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
