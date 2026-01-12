import pytest

from d20distribution import parse
from d20distribution.errors import DiceParseError


def equal(a: float, b: float, epsilon: float = 1e-6) -> bool:
    return abs(a - b) <= epsilon


def test_d20():
    distribution = parse("1d20")
    assert distribution.min() == 1
    assert distribution.max() == 20
    assert len(distribution.dist) == 20

    for d in range(distribution.min(), distribution.max() + 1):
        assert equal(distribution.get(d), 0.05)


def test_exceptions():
    with pytest.raises(ZeroDivisionError):
        parse("1d6 / 0")

    with pytest.raises(DiceParseError):
        parse("1d20 +")
