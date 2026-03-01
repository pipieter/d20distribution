import abc
import itertools
from collections import defaultdict
from collections.abc import Callable

import d20  # type: ignore
import numpy as np

from .distribution import DiceDistribution
from .errors import InvalidOperationError
from .limits import DICE_LIMITS, MODIFIED_DICE_LIMITS


class AbstractDistributionBuilder(abc.ABC):
    @abc.abstractmethod
    def distribution(self) -> DiceDistribution: ...

    def apply_operation(self, op: d20.ast.SetOperator) -> None:
        operation_functions = {
            "mi": self.apply_mi,
            "ma": self.apply_ma,
            "ro": self.apply_ro,
            "e": self.apply_e,
            "k": self.apply_k,
            "p": self.apply_p,
            # Unimplemented operations
            # "rr": self.apply_rr,
            # "ra": self.apply_ra,
        }

        operation: str = op.op
        selectors: list[d20.ast.SetSelector] = op.sels

        if operation not in operation_functions:
            raise InvalidOperationError(f"Unsupported operator: '{op.op}'")

        operation_functions[operation](selectors)

    @abc.abstractmethod
    def apply_mi(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_ma(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_ro(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_e(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_k(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_p(self, selectors: list[d20.ast.SetSelector]) -> None: ...

    @staticmethod
    def _matches_selector(value: int, selector: d20.ast.SetSelector) -> bool:
        cat: str | None = selector.cat

        if cat in ["", None]:
            return value == selector.num

        if cat == "<":
            return value < selector.num

        if cat == ">":
            return value > selector.num

        raise InvalidOperationError(f"Invalid operation found between value '{value}' and '{str(cat)}'")


class ConvolutionDistributionBuilder(AbstractDistributionBuilder):
    """
    A distribution builder that internally uses convolutions to calculate the distribution.
    These convolutions are typically much faster than iterating over all possibilities, but
    they are more limited in the operations they can perform.

    For more information on how convolutions work, see this blog post:
    https://blog.demofox.org/2025/01/05/dice-deconvolution-and-generating-functions/


    Raises:
        InvalidOperationError: When an invalid operator is passed as an argument. Certain operations are not possible using convolutions.
    """

    count: int
    sides: int
    convolution: list[float]

    def __init__(self, count: int, sides: int, operations: list[d20.ast.SetOperator]) -> None:
        if count * sides > DICE_LIMITS:
            raise InvalidOperationError("Too many dice!")

        super().__init__()
        self.count = count
        self.sides = sides
        self.convolution = [0] + [1 / sides] * sides

        for operation in operations:
            self.apply_operation(operation)

    def distribution(self) -> DiceDistribution:
        result = np.array([1.0])
        convolution = np.array(self.convolution)
        for _ in range(self.count):
            result = np.convolve(result, convolution)

        dist = {k: float(v) for k, v in enumerate(result) if abs(v) >= 1e-10}
        return DiceDistribution(dist)

    @staticmethod
    def supports_operation(operation: d20.ast.SetOperator) -> bool:
        invalid_operations = ["e", "ra"]
        invalid_selector_categories = ["h", "l"]

        if operation.op in invalid_operations:
            return False

        categories: list[str] = [sel.cat for sel in operation.sels]  # type: ignore
        if any(category in invalid_selector_categories for category in categories):
            return False

        return True

    def apply_mi(self, selectors: list[d20.ast.SetSelector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for mi: '{selector.cat}'")

            num: int = selector.num

            # Extend the convolution
            padding = num - len(self.convolution) + 1
            self.convolution.extend([0] * padding)
            for i in range(1, num):
                self.convolution[num] += self.convolution[i]
                self.convolution[i] = 0

    def apply_ma(self, selectors: list[d20.ast.SetSelector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for ma: '{selector.cat}'")

            num: int = selector.num
            for i in range(num + 1, len(self.convolution)):
                self.convolution[num] += self.convolution[i]
                self.convolution[i] = 0

    def apply_k(self, selectors: list[d20.ast.SetSelector]) -> None:
        for selector in selectors:
            for i in range(1, len(self.convolution)):
                if not self._matches_selector(i, selector):
                    self.convolution[0] += self.convolution[i]
                    self.convolution[i] = 0

    def apply_p(self, selectors: list[d20.ast.SetSelector]) -> None:
        for selector in selectors:
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    self.convolution[0] += self.convolution[i]
                    self.convolution[i] = 0

    def apply_ro(self, selectors: list[d20.ast.SetSelector]) -> None:
        for selector in selectors:
            reroll = 1 / self.sides
            odds_occurring = 0
            odds_not_occurring = 0
            sides_not_occurring = 0

            # Calculate the odds of event occuring
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    odds_occurring += self.convolution[i]
                else:
                    odds_not_occurring += self.convolution[i]
                    sides_not_occurring += 1

            # Re-calculate the odds
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    self.convolution[i] = odds_occurring * reroll
                else:
                    self.convolution[i] += odds_not_occurring * reroll / sides_not_occurring

    def apply_e(self, selectors: list[d20.ast.SetSelector]) -> None:
        raise InvalidOperationError(f"Explode operator not supported fro ConvolutionDistributionBuilder")


DiscreteKey = tuple[int, ...]


class DiscreteDistributionBuilder(AbstractDistributionBuilder):
    count: int
    sides: int
    dist: defaultdict[DiscreteKey, float]

    def __init__(self, count: int, sides: int, operations: list[d20.ast.SetOperator]) -> None:
        if sides**count > MODIFIED_DICE_LIMITS:
            raise InvalidOperationError("Too many dice!")

        super().__init__()
        self.count = count
        self.sides = sides
        self.dist = defaultdict(float)

        # Build distribution
        for raw_key in itertools.product(range(1, sides + 1), repeat=count):
            key = self._sort_key(raw_key)
            self.dist[key] += 1

        # Normalize the distribution
        total = sum(self.dist.values())
        for key in self.dist:
            self.dist[key] = self.dist[key] / total
        assert abs(sum(self.dist.values()) - 1) < 1e-8

        for operation in operations:
            self.apply_operation(operation)

    def distribution(self) -> DiceDistribution:
        dist = defaultdict[int, float](float)
        for key, value in self.dist.items():
            dist[sum(key)] += value
        return DiceDistribution(dict(dist))

    @staticmethod
    def _sort_key(key: DiscreteKey) -> DiscreteKey:
        return tuple(sorted(key))

    def _transform_keys(self, transform: Callable[[DiscreteKey], DiscreteKey]) -> None:
        new_dist = defaultdict[DiscreteKey, float](float)
        for key, value in self.dist.items():
            new_key = transform(key)
            new_key = self._sort_key(new_key)
            new_dist[new_key] += value
        self.dist = new_dist

    def apply_mi(self, selectors: list[d20.ast.SetSelector]) -> None:
        def apply_mi_to_key(key: DiscreteKey, min_value: int) -> DiscreteKey:
            return tuple([value if value >= selector.num else min_value for value in key])

        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for mi: '{selector.cat}'")

            min_value: int = selector.num
            self._transform_keys(lambda key: apply_mi_to_key(key, min_value))

    def apply_ma(self, selectors: list[d20.ast.SetSelector]) -> None:
        def apply_ma_to_key(key: DiscreteKey, max_value: int) -> DiscreteKey:
            return tuple([value if value <= selector.num else max_value for value in key])

        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for ma: '{selector.cat}'")

            max_value: int = selector.num
            self._transform_keys(lambda key: apply_ma_to_key(key, max_value))

    def apply_k(self, selectors: list[d20.ast.SetSelector]) -> None:
        def apply_k_to_key(key: DiscreteKey, selector: d20.ast.SetSelector) -> DiscreteKey:
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

        for selector in selectors:
            self._transform_keys(lambda key: apply_k_to_key(key, selector))

    def apply_p(self, selectors: list[d20.ast.SetSelector]) -> None:
        def apply_p_to_key(key: DiscreteKey, selector: d20.ast.SetSelector) -> DiscreteKey:
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

        for selector in selectors:
            self._transform_keys(lambda key: apply_p_to_key(key, selector))

    def apply_ro(self, selectors: list[d20.ast.SetSelector]) -> None:
        def get_reroll_dice_possibilities(dice: DiscreteKey, sides: int, category: str | None, num: int) -> list[DiscreteKey]:
            """
            Get all re-roll possibilities in a dice. This generates all possible results where the values matching
            the selector are re-rolled.
            """
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

        for selector in selectors:
            new_dist = defaultdict[DiscreteKey, float](float)
            for key in self.dist:
                odds = self.dist.get(key, 0)
                rerolls = get_reroll_dice_possibilities(key, self.sides, selector.cat, selector.num)
                for reroll in rerolls:
                    reroll_key = self._sort_key(reroll)
                    reroll_odds = odds / len(rerolls)
                    new_dist[reroll_key] += reroll_odds

            # Assert that the new distribution is also normalized
            assert abs(sum(new_dist.values()) - 1) < 1e-6

            self.dist = new_dist

    def apply_e(self, selectors: list[d20.ast.SetSelector]) -> None:
        def should_explode(selector: d20.ast.SetSelector, value: int) -> bool:
            if selector.cat is None:
                return value == selector.num
            if selector.cat == ">":
                return value > selector.num
            if selector.cat == "<":
                return value < selector.num

            raise InvalidOperationError(f"Invalid explode modifier selector '{selector.cat}'.")

        def apply_explode(
            dist: defaultdict[DiscreteKey, float],
            selector: d20.ast.SetSelector,
            base_odds: float,
            base_key: DiscreteKey,
            cutoff: float = 1e-8,
        ) -> defaultdict[DiscreteKey, float]:
            """
            Recursively applies the explode operator to a single distribution to get the distribution
            of the exploded dice.

            Args:
                dist (defaultdict[DiscreteKey, float]): The original distribution
                selector (d20.ast.SetSelector): The exploding criteria
                base_odds (float): The base odds of the current distribution. Should be initialized as 1.0.
                base_key (DiscreteKey): The base key. Should be initialized as ().
                cutoff (float, optional): The cut-off point after which explode is no longer applied. This is to prevent infinitely long executions. Defaults to 1e-6.

            Returns:
                defaultdict[DiscreteKey, float]: The new distribution of the exploded dice.
            """

            new_dist = defaultdict[DiscreteKey, float](float)

            for key in dist:
                new_key = base_key + key
                new_key = self._sort_key(new_key)
                new_odds = base_odds * dist.get(key, 0)
                if new_odds < cutoff:
                    new_dist[new_key] = cutoff
                    return new_dist

                if not should_explode(selector, sum(key)):
                    new_dist[new_key] += new_odds
                    continue
                exploded = apply_explode(dist, selector, new_odds, new_key)
                for key in exploded:
                    new_dist[key] += exploded.get(key, 0)

            return new_dist

        for selector in selectors:
            self.dist = apply_explode(self.dist, selector, 1.0, ())
