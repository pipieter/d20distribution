import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "sides",
    [
        ("20"),
        ("12"),
        ("10"),
        ("8"),
        ("6"),
        ("4"),
    ],
)
@pytest.mark.parametrize(
    "num",
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
def test_explode(benchmark: BenchmarkFixture, sides: str, num: str):
    expression = f"{num}d{sides}e{sides}"
    benchmark(parse, expression)
