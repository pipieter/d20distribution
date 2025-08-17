import copy
import math
from typing import Callable, Iterable


def combine(
    a: dict[int, float], b: dict[int, float], func: Callable[[int, int], int]
) -> dict[int, float]:
    result = dict()
    for ka, va in a.items():
        for kb, vb in b.items():
            key = func(ka, kb)
            result[key] = result.get(key, 0) + va * vb
    return result


class DiceDistribution(object):
    dist: dict[int, float]

    def __init__(self, values: dict[int, float]):
        self.dist = copy.deepcopy(values)
        if len(values) == 0:
            self.dist[0] = 1.0
            return

    def keys(self) -> Iterable[int]:
        """
        Get the possible dice values of the distribution.

        Returns:
            Iterable[int]: The possible dice values of the distribution sorted from lowest to highest.
        """
        return list(sorted(list(self.dist.keys())))

    def get(self, key: int) -> float:
        return self.dist.get(key, 0)

    def min(self) -> int:
        return min(self.keys())

    def max(self) -> int:
        return max(self.keys())

    def mean(self, mapping: Callable[[int], int] = lambda x: x) -> float:
        return sum([mapping(value) * odds for value, odds in self.dist.items()])

    def stdev(self) -> float:
        # variance = E(X^2) - E(X)^2
        # stdev = sqrt(variance)
        e_x2 = self.mean(mapping=lambda x: x**2)
        ex_2 = self.mean() ** 2
        return math.sqrt(e_x2 - ex_2)

    def __add__(self, other: "DiceDistribution") -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, other.dist, lambda a, b: a + b))

    def __sub__(self, other: "DiceDistribution") -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, other.dist, lambda a, b: a - b))

    def __mul__(self, other: "DiceDistribution") -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, other.dist, lambda a, b: a * b))

    def __floordiv__(self, other: "DiceDistribution") -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, other.dist, lambda a, b: a // b))

    def __neg__(self) -> "DiceDistribution":
        return DiceDistribution({-v: k for v, k in self.dist.items})

    def advantage(self) -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, self.dist, lambda a, b: max(a, b)))

    def disadvantage(self) -> "DiceDistribution":
        return DiceDistribution(combine(self.dist, self.dist, lambda a, b: min(a, b)))

    def __copy__(self) -> "DiceDistribution":
        return DiceDistribution(self.dist)

    def __deepcopy__(self) -> "DiceDistribution":
        return DiceDistribution(copy.deepcopy(self.dist))
