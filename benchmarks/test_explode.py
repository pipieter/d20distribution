import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "sides",
    [
        ("4"),
        ("6"),
        ("8"),
    ],
)
@pytest.mark.parametrize(
    "num",
    [
        ("4"),
        ("6"),
        ("8"),
    ],
)
def test_explode(benchmark: BenchmarkFixture, sides: str, num: str):
    expression = f"{num}d{sides}e{sides}"
    benchmark(parse, expression)
