import d20
import pytest

from d20distribution import parse


def equal(a: float, b: float, epsilon=1e-6) -> bool:
    return abs(a - b) <= epsilon


def test_d20():
    distribution = parse("1d20")
    assert distribution.min() == 1
    assert distribution.max() == 20
    assert len(distribution.values) == 20

    for d in range(distribution.min(), distribution.max() + 1):
        assert distribution.values.count(d) == 1


def test_exceptions():
    with pytest.raises(ZeroDivisionError):
        parse("1d6 / 0")

    with pytest.raises(d20.errors.RollSyntaxError):
        parse("1d20 +")


def test_dict():
    distribution = parse("3d6+5")
    dictionary = distribution.to_dict()

    assert set(distribution.keys()) == set(dictionary.keys())


def test_dict_d20():
    distribution = parse("1d20")
    dictionary = distribution.to_dict()

    for value in dictionary.values():
        assert equal(value, 0.05)
