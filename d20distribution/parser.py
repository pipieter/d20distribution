import d20  # pyright: ignore[reportMissingTypeStubs]

from .calculate import ConvolutionDistributionBuilder, DiscreteDistributionBuilder
from .distribution import Distribution
from .errors import DiceParseError


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

    # Attempt a roll first, to verify that the rolls are actually feasible
    try:
        d20.roll(expression)
    except d20.errors.RollSyntaxError:
        raise DiceParseError("There was a syntax error found while parsing the expression.")
    except Exception:
        raise DiceParseError("There was an error found while parsing the expression.")

    ast = d20.parse(expression)
    return _parse_ast(ast)


def _parse_dimensions(count: int, sides: str | int) -> tuple[int, int]:
    """Parse the dimensions from a d20.ast.Dice or d20.ast.OperatedDice

    Args:
        count (int): The count of the dice.
        sides (str | int): The sides of the dice.

    Returns:
        tuple[int, int]: The parsed values packed as a tuple, representing the count and sides respectively.
    """
    if sides == "%":
        sides = 100
    else:
        sides = int(sides)
    return count, sides


def _parse_ast(ast: d20.ast.Node) -> Distribution:
    """Parse a distribution from a d20 ast node.

    Args:
        ast (d20.ast.Node): The node to be parsed.

    Raises:
        DiceParseError: When an unsupported node is parsed.

    Returns:
        Distribution: The distribution matching the node.
    """

    if isinstance(ast, d20.ast.Expression):
        return _parse_ast(ast.roll)  # type: ignore

    if isinstance(ast, d20.ast.Literal):
        return Distribution({ast.value: 1.0})  # type: ignore

    if isinstance(ast, d20.ast.UnOp):
        if ast.op == "-":
            return -_parse_ast(ast.value)  # type: ignore
        if ast.op == "+":
            return _parse_ast(ast.value)  # type: ignore
        raise DiceParseError(f"Unsupported UnOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.BinOp):
        if ast.op == "+":
            return _parse_ast(ast.left) + _parse_ast(ast.right)
        if ast.op == "-":
            return _parse_ast(ast.left) - _parse_ast(ast.right)
        if ast.op == "*":
            return _parse_ast(ast.left) * _parse_ast(ast.right)
        if ast.op == "/":
            return _parse_ast(ast.left) // _parse_ast(ast.right)
        if ast.op == ">":
            return _parse_ast(ast.left) > _parse_ast(ast.right)
        if ast.op == ">=":
            return _parse_ast(ast.left) >= _parse_ast(ast.right)
        if ast.op == "<":
            return _parse_ast(ast.left) < _parse_ast(ast.right)
        if ast.op == "<=":
            return _parse_ast(ast.left) <= _parse_ast(ast.right)
        if ast.op == "==":
            return _parse_ast(ast.left).equals(_parse_ast(ast.right))
        if ast.op == "!=":
            return _parse_ast(ast.left).not_equals(_parse_ast(ast.right))

        raise DiceParseError(f"Unsupported BinOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.Parenthetical):
        return _parse_ast(ast.value)

    if isinstance(ast, d20.ast.Dice):
        count, sides = _parse_dimensions(ast.num, ast.size)
        operations = ast.operations

        contains_non_convolution_operation = any(not ConvolutionDistributionBuilder.supports_operation(op) for op in operations)

        if contains_non_convolution_operation:
            builder = DiscreteDistributionBuilder(count, sides, operations)
        else:
            builder = ConvolutionDistributionBuilder(count, sides, operations)

        return builder.distribution()

    raise DiceParseError(f"Unsupported node type '{type(ast)}'.")
