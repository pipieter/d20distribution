from .distribution import Distribution

def parse(expression: str) -> Distribution:
    """Parse a valid d20 expression to a distribution. The performance of the expression
    depends on the passed modifiers, as explained

    Args:
        expression (str): The dice expression, following the d20 style.

    Raises:
        DiceParseError: When an invalid expression is given.

    Returns:
        Distribution: A distribution built from the expression.
    """
    ...
