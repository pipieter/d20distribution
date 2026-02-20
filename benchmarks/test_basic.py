import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "expression",
    [
        ("1d20"),
        ("1d12"),
        ("1d10"),
        ("1d8"),
        ("1d6"),
        ("1d4"),
    ],
)
def test_basic(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)


@pytest.mark.parametrize(
    "expression",
    [
        ("1d20+1"),
        ("1d12+1"),
        ("1d10+1"),
        ("1d8+1"),
        ("1d6+1"),
        ("1d4+1"),
    ],
)
def test_basic_with_mod(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)
