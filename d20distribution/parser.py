import d20  # pyright: ignore[reportMissingTypeStubs]

from .calculate import ConvolutionDistributionBuilder, DiscreteDistributionBuilder
from .distribution import DiceDistribution
from .errors import DiceParseError


def parse(expression: str) -> DiceDistribution:
    # Attempt a roll first, to verify that the rolls are actually feasible
    try:
        d20.roll(expression)
    except d20.errors.RollSyntaxError:
        raise DiceParseError("There was a syntax error found while parsing the expression.")
    except Exception:
        raise DiceParseError("There was an error found while parsing the expression.")

    ast = d20.parse(expression, allow_comments=False)
    return parse_ast(ast)


def parse_dimensions(count: int, sides: str | int) -> tuple[int, int]:
    if sides == "%":
        sides = 100
    else:
        sides = int(sides)
    return count, sides


def parse_ast(ast: d20.ast.Node) -> DiceDistribution:
    if isinstance(ast, d20.ast.Expression):
        return parse_ast(ast.roll)  # type: ignore

    if isinstance(ast, d20.ast.Literal):
        return DiceDistribution({ast.value: 1.0})  # type: ignore

    if isinstance(ast, d20.ast.UnOp):
        if ast.op == "-":
            return -parse_ast(ast.value)  # type: ignore
        if ast.op == "+":
            return parse_ast(ast.value)  # type: ignore
        raise DiceParseError(f"Unsupported UnOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.BinOp):
        if ast.op == "+":
            return parse_ast(ast.left) + parse_ast(ast.right)  # type: ignore
        if ast.op == "-":
            return parse_ast(ast.left) - parse_ast(ast.right)  # type: ignore
        if ast.op == "*":
            return parse_ast(ast.left) * parse_ast(ast.right)  # type: ignore
        if ast.op == "/":
            return parse_ast(ast.left) // parse_ast(ast.right)  # type: ignore
        raise DiceParseError(f"Unsupported BinOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.Parenthetical):
        return parse_ast(ast.value)  # type: ignore

    if isinstance(ast, d20.ast.Dice):
        count, sides = parse_dimensions(ast.num, ast.size)
        builder = ConvolutionDistributionBuilder(count, sides, [])
        return builder.distribution()

    if isinstance(ast, d20.ast.OperatedDice):
        count, sides = parse_dimensions(ast.value.num, ast.value.size)  # type: ignore
        operations: list[d20.ast.SetOperator] = ast.operations  # type: ignore

        contains_non_convolution_operation = any(not ConvolutionDistributionBuilder.supports_operation(op) for op in operations)

        if contains_non_convolution_operation:
            builder = DiscreteDistributionBuilder(count, sides, operations)
        else:
            builder = ConvolutionDistributionBuilder(count, sides, operations)

        return builder.distribution()

    raise DiceParseError(f"Unsupported node type '{type(ast)}'.")
