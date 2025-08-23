from collections import defaultdict
from collections.abc import Callable
import itertools
import d20

from .distribution import DiceDistribution
from .errors import DiceParseError, InvalidOperationError
from .limits import DICE_LIMITS, MODIFIED_DICE_LIMITS


def parse(expression: str) -> DiceDistribution:
    # Attempt a roll first, to verify that the rolls are actually feasible
    try:
        d20.roll(expression)
    except d20.errors.RollSyntaxError:
        raise DiceParseError(
            "There was a syntax error found while parsing the expression."
        )
    except Exception:
        raise DiceParseError("There was an error found while parsing the expression.")

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


class DiscreteDiceDistributionBuilder(object):
    dist: defaultdict[tuple, float]

    def __init__(self):
        self.dist = defaultdict(float)

    def add(self, key: tuple, value: float) -> None:
        key = tuple(sorted(key))
        self.dist[key] += value

    def get(self, key: tuple) -> float:
        key = tuple(sorted(key))
        return self.dist[key]

    def keys(self) -> float:
        return self.dist.keys()

    def values(self) -> float:
        return self.dist.values()

    def build(self) -> "DiceDistribution":
        distribution = defaultdict(float)
        for key, value in self.dist.items():
            distribution[sum(key)] += value
        return DiceDistribution(dict(distribution))

    def transform_keys(self, transform: Callable[[tuple], tuple]) -> None:
        distribution = defaultdict(float)
        for key, value in self.dist.items():
            new_key = transform(key)
            distribution[new_key] += value
        self.dist = distribution


def calculate_dice_distribution_directly(
    num: int, sides: int, operations: list[d20.ast.SetOperator]
) -> DiceDistribution:
    # A limit is set to avoid extensive calculations. This function calculates the
    # odds of each possibility individually, which can grow exponentially for
    # a large number of dice.
    if sides**num > MODIFIED_DICE_LIMITS:
        raise InvalidOperationError(f"Modified dice are too large to calculate.")

    possibilities = sides**num
    products = itertools.product(range(1, sides + 1), repeat=num)
    distribution = DiscreteDiceDistributionBuilder()
    for product in products:
        distribution.add(tuple(product), 1 / possibilities)

    for op in operations:
        if op.op == "k":
            distribution.transform_keys(lambda k: apply_keep_to_key(k, op.sels[0]))
        elif op.op == "p":
            distribution.transform_keys(lambda k: apply_drop_to_key(k, op.sels[0]))
        elif op.op == "mi":
            distribution.transform_keys(lambda k: apply_min_to_key(k, op.sels[0].num))
        elif op.op == "ma":
            distribution.transform_keys(lambda k: apply_max_to_key(k, op.sels[0].num))
        elif op.op == "ro":
            distribution = apply_ro(distribution, sides, op.sels[0])
        else:
            raise InvalidOperationError(f"Unsupported dice modifier '{op.op}'.")

    return distribution.build()


def apply_keep_to_key(key: tuple, selector: d20.ast.SetSelector) -> tuple:
    if selector.cat is None:
        # Keep all values matching exactly selector.num
        return tuple([p for p in key if p == selector.num])

    if selector.cat == "<":
        # Keep all values smaller than selector.num
        return tuple([p for p in key if p < selector.num])

    if selector.cat == ">":
        # Keep all values greater than selector.num
        return tuple([p for p in key if p > selector.num])

    if selector.cat == "l":
        # Keep lowest selector.num values
        key = list(sorted(list(key), reverse=False))
        key = key[: selector.num]
        return tuple(key)

    if selector.cat == "h":
        # Keep highest selector.num values
        key = list(sorted(list(key), reverse=True))
        key = key[: selector.num]
        return tuple(key)

    raise InvalidOperationError(f"Invalid keep modifier selector '{selector.cat}'.")


def apply_drop_to_key(key: tuple, selector: d20.ast.SetSelector) -> tuple:
    if selector.cat is None:
        # Drop all values matching exactly selector.num
        return tuple([p for p in key if p != selector.num])

    if selector.cat == "<":
        # Drop all values smaller than selector.num
        return tuple([p for p in key if p >= selector.num])

    if selector.cat == ">":
        # Drop all values greater than selector.num
        return tuple([p for p in key if p <= selector.num])

    if selector.cat == "l":
        # Drop lowest selector.num values
        key = list(sorted(list(key), reverse=False))
        key = key[selector.num :]
        return tuple(key)

    if selector.cat == "h":
        # Drop highest selector.num values
        key = list(sorted(list(key), reverse=True))
        key = key[selector.num :]
        return tuple(key)

    raise InvalidOperationError(f"Invalid drop modifier selector '{selector.cat}'.")


def apply_min_to_key(key: tuple, min_value: int) -> tuple:
    return tuple([value if value >= min_value else min_value for value in key])


def apply_max_to_key(key: tuple, max_value: int) -> tuple:
    return tuple([value if value <= max_value else max_value for value in key])


def apply_ro(
    distribution: DiscreteDiceDistributionBuilder,
    sides: int,
    selector: d20.ast.SetSelector,
) -> DiscreteDiceDistributionBuilder:
    newdist = DiscreteDiceDistributionBuilder()
    for key in distribution.keys():
        odds = distribution.get(key)
        rerolls = get_reroll_dice_possibilities(key, sides, selector.cat, selector.num)
        for reroll in rerolls:
            newdist.add(reroll, odds / len(rerolls))

    # Assert distribution is also normalized
    assert abs(sum(newdist.values()) - 1) < 1e-6

    return newdist


def get_reroll_dice_possibilities(
    dice: tuple, sides: int, category: str | None, num: int
) -> list[tuple]:
    if len(dice) == 0:
        return [()]

    # Handle h and l separately, as they depend on the dice ordering
    if category in ["h", "l"]:
        if num <= 0:
            return [dice]

        if category == "h":
            dice = tuple(sorted(dice, reverse=True))
        else:
            dice = tuple(sorted(dice, reverse=False))

        _, *rest = dice
        combinations = get_reroll_dice_possibilities(
            tuple(rest), sides, category, num - 1
        )
        outcomes: list[tuple] = []

        for combination in combinations:
            for roll in range(1, sides + 1):
                outcomes.append((roll,) + combination)

        return outcomes

    first, *rest = dice
    combinations = get_reroll_dice_possibilities(tuple(rest), sides, category, num)
    outcomes = []

    if (
        (category is None and first == num)
        or (category == ">" and first > num)
        or (category == "<" and first < num)
    ):
        for combination in combinations:
            for roll in range(1, sides + 1):
                outcomes.append((roll,) + combination)
    else:
        for combination in combinations:
            outcomes.append((first,) + combination)

    return outcomes
