import itertools
import d20

from .distribution import DiceDistribution
from .errors import DiceParseError, InvalidOperationError
from .limits import DICE_LIMITS, MODIFIED_DICE_LIMITS


def parse(expression: str) -> DiceDistribution:
    # Attempt a roll first, to verify that the rolls are actually feasible
    d20.roll(expression)

    ast = d20.parse(expression, allow_comments=False)
    return parse_ast(ast)


def parse_ast(ast: d20.ast.Node) -> DiceDistribution:
    if isinstance(ast, d20.ast.Expression):
        return parse_ast(ast.roll)

    if isinstance(ast, d20.ast.Literal):
        return DiceDistribution({ast.value: 1.0})

    if isinstance(ast, d20.ast.UnOp):
        if ast.op == "-":
            return -parse_ast(ast.value)
        if ast.op == "+":
            return parse_ast(ast.value)
        raise DiceParseError(f"Unsupported UnOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.BinOp):
        if ast.op == "+":
            return parse_ast(ast.left) + parse_ast(ast.right)
        if ast.op == "-":
            return parse_ast(ast.left) - parse_ast(ast.right)
        if ast.op == "*":
            return parse_ast(ast.left) * parse_ast(ast.right)
        if ast.op == "/":
            return parse_ast(ast.left) // parse_ast(ast.right)
        raise DiceParseError(f"Unsupported BinOp operator '{ast.op}'.")

    if isinstance(ast, d20.ast.Dice):
        return calculate_dice_distribution(ast.num, ast.size, [])

    if isinstance(ast, d20.ast.OperatedDice):
        return calculate_dice_distribution(
            ast.value.num, ast.value.size, ast.operations
        )

    if isinstance(ast, d20.ast.Parenthetical):
        return parse_ast(ast.value)

    raise DiceParseError(f"Unsupported node type '{type(ast)}'.")


def calculate_dice_distribution(
    num: int, sides: int, operations: list[d20.ast.SetOperator]
) -> DiceDistribution:
    if len(operations) > 0:
        return calculate_dice_distribution_directly(num, sides, operations)

    if sides * num > DICE_LIMITS:
        raise InvalidOperationError(f"Dice are too large to calculate.")

    distribution = DiceDistribution({})
    for _ in range(num):
        distribution = distribution + DiceDistribution(
            {k: 1 / sides for k in range(1, sides + 1)}
        )
    return distribution


def calculate_dice_distribution_directly(
    num: int, sides: int, operations: list[d20.ast.SetOperator]
) -> DiceDistribution:
    # A limit is set to avoid extensive calculations. This function calculates the
    # odds of each possibility individually, which can grow exponentially for
    # a large number of dice.
    if sides**num > MODIFIED_DICE_LIMITS:
        raise InvalidOperationError(f"Modified dice are too large to calculate.")

    possibilities = itertools.product(range(1, sides + 1), repeat=num)

    for operation in operations:
        if operation.op == "k":
            sel = operation.sels[0]
            possibilities = map(lambda pos: apply_keep(pos, sel), possibilities)
        elif operation.op == "p":
            sel = operation.sels[0]
            possibilities = map(lambda pos: apply_drop(pos, sel), possibilities)
        elif operation.op == "mi":
            value = operation.sels[0].num
            possibilities = map(lambda pos: apply_min(pos, value), possibilities)
        elif operation.op == "ma":
            value = operation.sels[0].num
            possibilities = map(lambda pos: apply_max(pos, value), possibilities)
        else:
            raise InvalidOperationError(f"Unsupported dice modifier '{operation.op}'.")

    values = list(map(sum, possibilities))
    keys = set(values)
    return DiceDistribution({key: values.count(key) / len(values) for key in keys})


def apply_keep(possibility: tuple, selector: d20.ast.SetSelector) -> tuple:
    if selector.cat is None:
        # Keep all values matching exactly selector.num
        return tuple([p for p in possibility if p == selector.num])

    if selector.cat == "<":
        # Keep all values smaller than selector.num
        return tuple([p for p in possibility if p < selector.num])

    if selector.cat == ">":
        # Keep all values greater than selector.num
        return tuple([p for p in possibility if p > selector.num])

    if selector.cat == "l":
        # Keep lowest selector.num values
        possibility = list(sorted(list(possibility), reverse=False))
        possibility = possibility[: selector.num]
        return tuple(possibility)

    if selector.cat == "h":
        # Keep highest selector.num values
        possibility = list(sorted(list(possibility), reverse=True))
        possibility = possibility[: selector.num]
        return tuple(possibility)

    raise InvalidOperationError(f"Invalid keep modifier selector '{selector.cat}'.")


def apply_drop(possibility: tuple, selector: d20.ast.SetSelector) -> tuple:
    if selector.cat is None:
        # Drop all values matching exactly selector.num
        return tuple([p for p in possibility if p != selector.num])

    if selector.cat == "<":
        # Drop all values smaller than selector.num
        return tuple([p for p in possibility if p >= selector.num])

    if selector.cat == ">":
        # Drop all values greater than selector.num
        return tuple([p for p in possibility if p <= selector.num])

    if selector.cat == "l":
        # Drop lowest selector.num values
        possibility = list(sorted(list(possibility), reverse=False))
        possibility = possibility[selector.num :]
        return tuple(possibility)

    if selector.cat == "h":
        # Drop highest selector.num values
        possibility = list(sorted(list(possibility), reverse=True))
        possibility = possibility[selector.num :]
        return tuple(possibility)

    raise InvalidOperationError(f"Invalid drop modifier selector '{selector.cat}'.")


def apply_min(possibility: tuple, min_value: tuple) -> tuple:
    return tuple([value if value >= min_value else min_value for value in possibility])


def apply_max(possibility: tuple, max_value: tuple) -> tuple:
    return tuple([value if value <= max_value else max_value for value in possibility])
