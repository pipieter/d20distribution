import pytest

from d20distribution import parse
from d20distribution.errors import InvalidOperationError


def test_limits():
    # Limits are defined to prevent calculations from taking too long.
    # These limits are defined in d20distribution.limits, and are
    # different for modified dice and non-modified dice.

    parse("50d50") # Unmodified
    parse("4d6kh3")  # Modified, 1296 possibilities

    with pytest.raises(InvalidOperationError):
        parse("6d6kh3")  # 46656 possibilities

    with pytest.raises(InvalidOperationError):
        parse("400d400")