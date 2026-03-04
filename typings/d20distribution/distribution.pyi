from typing import Callable, Iterable, Optional

class Distribution:
    _dist: dict[int, float]
    def __init__(self, values: Optional[dict[int, float]] = ...) -> None: ...
    def keys(self) -> Iterable[int]:
        """Get the possible dice sums of the distribution.

        Returns:
            Iterable[int]: The possible dice sums of the distribution sorted from lowest to highest.
        """
        ...

    def values(self) -> Iterable[float]:
        """Get all stored probability values of the distribution.

        Returns:
            Iterable[float]: The possible probability values of the distribution, in no particular order.
        """
        ...

    def get(self, key: int) -> float:
        """Get the probability of a single key.

        Args:
            key (int): The key to retrieve.

        Returns:
            float: The stored probability of the key, or zero if the key is not present.
        """
        ...

    def get_at_least(self, key: int) -> float:
        """Get the probability of getting at least the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at least the key, inclusive of the key.
        """
        ...

    def get_at_most(self, key: int) -> float:
        """Get the probability of getting at most the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at most the key, inclusive of the key.
        """
        ...

    def min(self) -> int:
        """Get the minimum key in the distribution.

        Returns:
            int: The lowest key in the distribution.
        """
        ...

    def max(self) -> int:
        """Get the maximum key in the distribution.

        Returns:
            int: The highest key in the distribution.
        """
        ...

    def mean(self, key_mapping: Optional[Callable[[int], int]] = ...) -> float:
        """Get the mean value of the distribution.

        Args:
            mapping (Optional[Callable[[int], int]], optional): An optional function to perform on the keys of the distribution. Defaults to None.

        Returns:
            float: The mean of the distribution.
        """
        ...

    def stdev(self) -> float:
        """Get the standard deviation of the distribution.

        Returns:
            float: The standard deviation of the distribution.
        """
        ...

    def __add__(self, other: Distribution) -> Distribution:
        """Adds two distributions together, e.g. 1d20 + 1d4.

        Args:
            other (Distribution): The other distribution to add.

        Returns:
            Distribution: The sum of the two distributions.
        """
        ...

    def __sub__(self, other: Distribution) -> Distribution:
        """Subtract two distributions from each other, e.g. 1d20 - 1d4.

        Args:
            other (Distribution): The other distribution to subtract.

        Returns:
            Distribution: The difference of the two distributions.
        """
        ...

    def __mul__(self, other: Distribution) -> Distribution:
        """Multiply two distributions together, e.g. 1d20 * 1d4.

        Args:
            other (Distribution): The other distribution to multiply.

        Returns:
            Distribution: The product of the two distributions.
        """
        ...

    def __floordiv__(self, other: Distribution) -> Distribution:
        """Divide two distributions from each other, e.g. 1d20 / 1d4. Note that this is the floor
        division, and not the true division, as distribution keys need to be integers.

        Args:
            other (Distribution): The divisor of the division.

        Raises:
            ZeroDivisionError: When one of the possible keys in the divisor is zero.

        Returns:
            Distribution: The division of the two distributions.
        """
        ...

    def __neg__(self) -> Distribution:
        """Negate the values of a distribution.

        Returns:
            Distribution: The distribution with the signs of all of its keys reversed.
        """
        ...

    def advantage(self, count: int = ...) -> Distribution:
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
        ...

    def disadvantage(self, count: int = ...) -> Distribution:
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
        ...

    def __copy__(self) -> Distribution:
        """Create a copy of the distribution. All values of the other distribution
        are deep-copied.

        Returns:
            Distribution: A copy of the distribution.
        """
        ...

    def __deepcopy__(self) -> Distribution:
        """Creates a deep copy of the distribution.

        Returns:
            Distribution: A deep copy of the distribution.
        """
        ...
