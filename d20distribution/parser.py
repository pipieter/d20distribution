import itertools
from collections import defaultdict
from collections.abc import Callable, Iterable

import d20  # pyright: ignore[reportMissingTypeStubs]
import numpy as np

from .distribution import DiceDistribution
from .errors import DiceParseError, InvalidOperationError
from .limits import DICE_LIMITS, MODIFIED_DICE_LIMITS

DiscreteKey = tuple[int, ...]


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

    if isinstance(ast, d20.ast.Dice):
        return calculate_dice_distribution(ast.num, ast.size, [])  # type: ignore

    if isinstance(ast, d20.ast.OperatedDice):
        return calculate_dice_distribution(ast.value.num, ast.value.size, ast.operations)  # type: ignore

    if isinstance(ast, d20.ast.Parenthetical):
        return parse_ast(ast.value)  # type: ignore

    raise DiceParseError(f"Unsupported node type '{type(ast)}'.")


def calculate_dice_distribution(num: int, sides: int, operations: list[d20.ast.SetOperator]) -> DiceDistribution:
    if len(operations) > 0:
        return calculate_dice_distribution_directly(num, sides, operations)

    if sides * num > DICE_LIMITS:
        raise InvalidOperationError(f"Dice are too large to calculate.")

    if num == 0 or sides == 0:
        return DiceDistribution({0: 1})

    # The uniform dice distributions will be calculated using polynomial convolutions
    # For more information, see this blog post:
    # https://blog.demofox.org/2025/01/05/dice-deconvolution-and-generating-functions/

    min_value = num
    max_value = num * sides

    single_conv = np.array([1 / sides for _ in range(sides)])
    combined_conv = single_conv

    for _ in range(num - 1):
        combined_conv = np.convolve(combined_conv, single_conv)

    # Remember to shift the values by min_value
    distribution = {i: float(combined_conv[i - min_value]) for i in range(min_value, max_value + 1)}
    return DiceDistribution(distribution)


class DiscreteDiceDistributionBuilder(object):
    dist: defaultdict[DiscreteKey, float]

    def __init__(self):
        self.dist = defaultdict(float)

    def add(self, key: DiscreteKey, value: float) -> None:
        key = tuple(sorted(key))
        self.dist[key] += value

    def get(self, key: DiscreteKey) -> float:
        key = tuple(sorted(key))
        return self.dist[key]

    def keys(self) -> Iterable[DiscreteKey]:
        return self.dist.keys()

    def values(self) -> Iterable[float]:
        return self.dist.values()

    def build(self) -> "DiceDistribution":
        distribution = defaultdict[int, float](float)
        for key, value in self.dist.items():
            distribution[sum(key)] += value
        return DiceDistribution(dict(distribution))

    def transform_keys(self, transform: Callable[[DiscreteKey], DiscreteKey]) -> None:
        distribution = defaultdict[DiscreteKey, float](float)
        for key, value in self.dist.items():
            new_key = transform(key)
            distribution[new_key] += value
        self.dist = distribution


def calculate_dice_distribution_directly(num: int, sides: int, operations: list[d20.ast.SetOperator]) -> DiceDistribution:
    # If the dice count (num) isn't modified (no keep/drop or high/low operators),
    # we can compute XdY as X separate 1dY rolls added together (e.g. 2d8 === 1d8 + 1d8).
    # Instead of generating every possible combination of rolls, we can reuse the single-die distribution and combine it repeatedly.
    # This produces the same result but computes much faster. (O(X*Y) instead of O(Y^X))
    expression_manipulates_dice_count = any(op.op in ["k", "p"] for op in operations)
    expression_has_set_selector = any(op.sels[0] in ["h", "l"] for op in operations)

    if not expression_manipulates_dice_count and not expression_has_set_selector and num > 1:
        if sides * num > DICE_LIMITS:
            raise InvalidOperationError("Modified dice are too large to calculate.")

        dist = calculate_dice_distribution_directly(1, sides, operations)
        for _ in range(num - 1):
            dist += calculate_dice_distribution_directly(1, sides, operations)
        return dist

    # A limit is set to avoid extensive calculations. This function calculates the
    # odds of each possibility individually, which can grow exponentially for
    # a large number of dice.
    if sides**num > MODIFIED_DICE_LIMITS:
        raise InvalidOperationError("Modified dice are too large to calculate.")

    possibilities = sides**num
    products = itertools.product(range(1, sides + 1), repeat=num)
    distribution = DiscreteDiceDistributionBuilder()
    for product in products:
        distribution.add(tuple(product), 1 / possibilities)

    for op in operations:
        if op.op == "k":
            distribution.transform_keys(lambda k: apply_keep_to_key(k, op.sels[0]))  # type: ignore
        elif op.op == "p":
            distribution.transform_keys(lambda k: apply_drop_to_key(k, op.sels[0]))  # type: ignore
        elif op.op == "mi":
            distribution.transform_keys(lambda k: apply_min_to_key(k, op.sels[0].num))  # type: ignore
        elif op.op == "ma":
            distribution.transform_keys(lambda k: apply_max_to_key(k, op.sels[0].num))  # type: ignore
        elif op.op == "ro":
            distribution = apply_ro(distribution, sides, op.sels[0])  # type: ignore
        elif op.op == "e":
            distribution = apply_explode(distribution, op.sels[0])  # type: ignore
        else:
            raise InvalidOperationError(f"Unsupported dice modifier '{op.op}'.")

    return distribution.build()


def apply_keep_to_key(key: DiscreteKey, selector: d20.ast.SetSelector) -> DiscreteKey:
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
        key = tuple(sorted(list(key), reverse=False))
        key = key[: selector.num]
        return key

    if selector.cat == "h":
        # Keep highest selector.num values
        key = tuple(sorted(list(key), reverse=True))
        key = key[: selector.num]
        return key

    raise InvalidOperationError(f"Invalid keep modifier selector '{selector.cat}'.")


def apply_drop_to_key(key: DiscreteKey, selector: d20.ast.SetSelector) -> DiscreteKey:
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
        key = tuple(sorted(list(key), reverse=False))
        key = key[selector.num :]
        return key

    if selector.cat == "h":
        # Drop highest selector.num values
        key = tuple(sorted(list(key), reverse=True))
        key = key[selector.num :]
        return key

    raise InvalidOperationError(f"Invalid drop modifier selector '{selector.cat}'.")


def apply_min_to_key(key: DiscreteKey, min_value: int) -> DiscreteKey:
    return tuple([value if value >= min_value else min_value for value in key])


def apply_max_to_key(key: DiscreteKey, max_value: int) -> DiscreteKey:
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


def get_reroll_dice_possibilities(dice: DiscreteKey, sides: int, category: str | None, num: int) -> list[DiscreteKey]:
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
        combinations = get_reroll_dice_possibilities(tuple(rest), sides, category, num - 1)
        outcomes: list[DiscreteKey] = []

        for combination in combinations:
            for roll in range(1, sides + 1):
                outcomes.append((roll,) + combination)

        return outcomes

    first, *rest = dice
    combinations = get_reroll_dice_possibilities(tuple(rest), sides, category, num)
    outcomes = []

    if (category is None and first == num) or (category == ">" and first > num) or (category == "<" and first < num):
        for combination in combinations:
            for roll in range(1, sides + 1):
                outcomes.append((roll,) + combination)
    else:
        for combination in combinations:
            outcomes.append((first,) + combination)

    return outcomes


def apply_explode(
    distribution: DiscreteDiceDistributionBuilder,
    selector: d20.ast.SetSelector,
    base_odds: float = 1.0,
    base_key: DiscreteKey = (),
) -> DiscreteDiceDistributionBuilder:
    newdist = DiscreteDiceDistributionBuilder()

    for key in distribution.keys():
        new_key = base_key + key
        new_odds = base_odds * distribution.get(key)
        if new_odds < 1e-6:
            return newdist

        if not _should_explode(selector, sum(key)):
            newdist.add(new_key, new_odds)
            continue

        exploded = apply_explode(distribution, selector, new_odds, new_key)
        for key in exploded.keys():
            newdist.add(key, exploded.get(key))

    return newdist


def _should_explode(selector: d20.ast.SetSelector, value: int) -> bool:
    if selector.cat is None:
        return value == selector.num
    if selector.cat == ">":
        return value > selector.num
    if selector.cat == "<":
        return value < selector.num

    raise InvalidOperationError(f"Invalid explode modifier selector '{selector.cat}'.")
