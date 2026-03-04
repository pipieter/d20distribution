import copy
import math
from typing import Callable, Iterable, Optional

from .errors import InvalidOperationError


def _combine_dictionaries(a: dict[int, float], b: dict[int, float], func: Callable[[int, int], int]) -> dict[int, float]:
    """Combine two dictionaries by combining their keys pair-wise using a combination function.

    Args:
        a (dict[int, float]): The first dictionary to merge.
        b (dict[int, float]): The second dictionary to merge.
        func (Callable[[int, int], int]): A function to combine keys. This function should return a new valid key.

    Returns:
        dict[int, float]: The combined dictionary.
    """

    result = dict[int, float]()
    for ka, va in a.items():
        for kb, vb in b.items():
            key = func(ka, kb)
            result[key] = result.get(key, 0) + va * vb
    return result


class Distribution(object):
    _dist: dict[int, float]

    def __init__(self, values: Optional[dict[int, float]] = None):
        if values:
            self._dist = copy.deepcopy(values)
        else:
            self._dist = {0: 1.0}

    def keys(self) -> Iterable[int]:
        """Get the possible dice sums of the distribution.

        Returns:
            Iterable[int]: The possible dice sums of the distribution sorted from lowest to highest.
        """
        return list(sorted(list(self._dist.keys())))

    def values(self) -> Iterable[float]:
        """Get all stored probability values of the distribution.

        Returns:
            Iterable[float]: The possible probability values of the distribution, in no particular order.
        """
        return list(self._dist.values())

    def get(self, key: int) -> float:
        """Get the probability of a single key.

        Args:
            key (int): The key to retrieve.

        Returns:
            float: The stored probability of the key, or zero if the key is not present.
        """

        return self._dist.get(key, 0)

    def get_at_least(self, key: int) -> float:
        """Get the probability of getting at least the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at least the key, inclusive of the key.
        """
        keys = [k for k in self.keys() if k >= key]
        if len(keys) == 0:
            return 0
        return sum(self.get(k) for k in keys)

    def get_at_most(self, key: int) -> float:
        """Get the probability of getting at most the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at most the key, inclusive of the key.
        """
        keys = [k for k in self.keys() if k <= key]
        if len(keys) == 0:
            return 0
        return sum(self.get(k) for k in keys)

    def min(self) -> int:
        """Get the minimum key in the distribution.

        Returns:
            int: The lowest key in the distribution.
        """

        return min(self.keys())

    def max(self) -> int:
        """Get the maximum key in the distribution.

        Returns:
            int: The highest key in the distribution.
        """
        return max(self.keys())

    def mean(self, key_mapping: Optional[Callable[[int], int]] = None) -> float:
        """Get the mean value of the distribution.

        Args:
            mapping (Optional[Callable[[int], int]], optional): An optional function to perform on the keys of the distribution. Defaults to None.

        Returns:
            float: The mean of the distribution.
        """

        if key_mapping is None:
            key_mapping = lambda x: x
        return sum([key_mapping(key) * probability for key, probability in self._dist.items()])

    def stdev(self) -> float:
        """Get the standard deviation of the distribution.

        Returns:
            float: The standard deviation of the distribution.
        """
        # variance = E(X^2) - E(X)^2
        # stdev = sqrt(variance)
        e_x2 = self.mean(key_mapping=lambda x: x**2)
        ex_2 = self.mean() ** 2
        return math.sqrt(abs(e_x2 - ex_2))

    def __add__(self, other: "Distribution") -> "Distribution":
        """Adds two distributions together, e.g. 1d20 + 1d4.

        Args:
            other (Distribution): The other distribution to add.

        Returns:
            Distribution: The sum of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a + b))

    def __sub__(self, other: "Distribution") -> "Distribution":
        """Subtract two distributions from each other, e.g. 1d20 - 1d4.

        Args:
            other (Distribution): The other distribution to subtract.

        Returns:
            Distribution: The difference of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a - b))

    def __mul__(self, other: "Distribution") -> "Distribution":
        """Multiply two distributions together, e.g. 1d20 * 1d4.

        Args:
            other (Distribution): The other distribution to multiply.

        Returns:
            Distribution: The product of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a * b))

    def __floordiv__(self, other: "Distribution") -> "Distribution":
        """Divide two distributions from each other, e.g. 1d20 / 1d4. Note that this is the floor
        division, and not the true division, as distribution keys need to be integers.

        Args:
            other (Distribution): The divisor of the division.

        Raises:
            ZeroDivisionError: When one of the possible keys in the divisor is zero.

        Returns:
            Distribution: The division of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a // b))

    def __neg__(self) -> "Distribution":
        """Negate the values of a distribution.

        Returns:
            Distribution: The distribution with the signs of all of its keys reversed.
        """
        return Distribution({-v: k for v, k in self._dist.items()})

    def advantage(self, count: int = 2) -> "Distribution":
        """Calculate the advantage of a distribution. This means that for all possible
        keys in the distribution, a pairwise combination is taken where the highest value
         is taken.

        Args:
            count (int, optional): The amount of dice to be rolled for which the highest
            is taken. For example, if count is three then three dice are rolled and the
            highest is taken. Defaults to 2.

        Raises:
            InvalidOperationError: If less than one dice count is given.

        Returns:
            Distribution: The distribution rolled multiple times, with the highest values
            taken each time.
        """
        if count < 1:
            raise InvalidOperationError(f"Rolling with advantage requires at least one roll, instead received {count}.")

        result = copy.copy(self._dist)
        for _ in range(1, count):
            result = _combine_dictionaries(result, self._dist, lambda a, b: max(a, b))
        return Distribution(result)

    def disadvantage(self, count: int = 2) -> "Distribution":
        """Calculate the disadvantage of a distribution. This means that for all possible
        keys in the distribution, a pairwise combination is taken where the lowest value
         is taken.

        Args:
            count (int, optional): The amount of dice to be rolled for which the lowest
            is taken. For example, if count is three then three dice are rolled and the
            lowest is taken. Defaults to 2.

        Raises:
            InvalidOperationError: If less than one dice count is given.

        Returns:
            Distribution: The distribution rolled multiple times, with the lowest values
            taken each time.
        """

        if count < 1:
            raise InvalidOperationError(f"Rolling with disadvantage requires at least one roll, instead received {count}.")

        result = copy.copy(self._dist)
        for _ in range(1, count):
            result = _combine_dictionaries(result, self._dist, lambda a, b: min(a, b))
        return Distribution(result)

    def __copy__(self) -> "Distribution":
        """Create a copy of the distribution. All values of the other distribution
        are deep-copied.

        Returns:
            Distribution: A copy of the distribution.
        """
        return Distribution(self._dist)

    def __deepcopy__(self) -> "Distribution":
        """Creates a deep copy of the distribution.

        Returns:
            Distribution: A deep copy of the distribution.
        """
        return Distribution(copy.deepcopy(self._dist))
