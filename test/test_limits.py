import pytest

from d20distribution import parse
from d20distribution.errors import InvalidOperationError


def test_limits():
    # A limit is set to 8192 to limit the sizes of modified dice
    # This is to prevent the complex calculations from taking too long

    parse("4d6kh3")  # 1296 possibilities

    with pytest.raises(InvalidOperationError):
        parse("6d6kh3")  # 46656 possibilities
