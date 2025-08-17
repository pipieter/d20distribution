import copy
import itertools
import math
from typing import Callable, Iterable

from .errors import InvalidOperationError


class DiceDistribution(object):
    values: list[int]

    def __init__(self, values: list[int]):
        self.set_values(values)

    def set_values(self, values: list[int]):
        self.values = [*values]

        # Ensure distribution contains at least one element
        if len(self.values) == 0:
            self.values = [0]

    def keys(self) -> Iterable[int]:
        """
        Get the possible dice values of the distribution.

        Returns:
            Iterable[int]: The possible dice values of the distribution sorted from lowest to highest.
        """
        return list(sorted(list(set(self.values))))

    def min(self) -> int:
        return min(self.values)

    def max(self) -> int:
        return max(self.values)

    def mean(self, mapping: Callable[[int], int] = lambda x: x) -> float:
        return sum([mapping(value) / len(self.values) for value in self.values])

    def stdev(self) -> float:
        # variance = E(X^2) - E(X)^2
        # stdev = sqrt(variance)
        e_x2 = self.mean(mapping=lambda x: x**2)
        ex_2 = self.mean() ** 2
        return math.sqrt(e_x2 - ex_2)

    def to_dict(self) -> dict[int, float]:
        keys = set(self.values)
        return {key: self.values.count(key) / len(self.values) for key in keys}

    def __add__(self, other: "DiceDistribution") -> "DiceDistribution":
        product = itertools.product(self.keys(), other.keys())
        return DiceDistribution([a + b for a, b in product])

    def __sub__(self, other: "DiceDistribution") -> "DiceDistribution":
        product = itertools.product(self.keys(), other.keys())
        return DiceDistribution([a - b for a, b in product])

    def __mul__(self, other: "DiceDistribution") -> "DiceDistribution":
        product = itertools.product(self.keys(), other.keys())
        return DiceDistribution([a * b for a, b in product])

    def __floordiv__(self, other: "DiceDistribution") -> "DiceDistribution":
        product = itertools.product(self.keys(), other.keys())
        return DiceDistribution([a // b for a, b in product])

    def __neg__(self) -> "DiceDistribution":
        return DiceDistribution([-value for value in self.values])

    def advantage(self) -> "DiceDistribution":
        product = itertools.product(self.keys(), self.keys())
        return DiceDistribution([max(a, b) for a, b in product])

    def disadvantage(self) -> "DiceDistribution":
        product = itertools.product(self.keys(), self.keys())
        return DiceDistribution([min(a, b) for a, b in product])

    def __copy__(self) -> "DiceDistribution":
        return DiceDistribution(self.values)

    def __deepcopy__(self) -> "DiceDistribution":
        return DiceDistribution(copy.deepcopy(self.values))
