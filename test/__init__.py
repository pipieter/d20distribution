from typing import Union

from d20distribution.distribution import Distribution

TNumeric = Union[int, float]


class Approx:
    _value: TNumeric
    _eps: TNumeric

    def __init__(self, value: TNumeric, eps: TNumeric) -> None:
        super().__init__()
        self._value = value
        self._eps = eps

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TNumeric):
            return abs(other - self._value) <= self._eps

        return super().__eq__(other)


def approx(value: TNumeric, eps: TNumeric = 1e-6):
    """Re-implementation of pytest's approx, with typing support"""
    return Approx(value, eps)


def assert_distribution(distribution: Distribution, values: list[tuple[int, float]], eps: float = 1e-4) -> None:
    for roll, expected in values:
        actual = distribution.get(roll)
        assert actual == approx(expected, eps), f"For key '{roll}' expected {expected}, but received {actual}"
