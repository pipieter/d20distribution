import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "dice",
    [
        ("12"),
        ("10"),
        ("8"),
        ("6"),
        ("4"),
    ],
)
@pytest.mark.parametrize(
    "count",
    [
        ("100"),
        ("20"),
        ("12"),
        ("10"),
        ("8"),
        ("6"),
        ("4"),
    ],
)
def test_explode(benchmark: BenchmarkFixture, dice: str, count: str):
    expression = f"{count}d{dice}e{dice}"
    benchmark(parse, expression)
