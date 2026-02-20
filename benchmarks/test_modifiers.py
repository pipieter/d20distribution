import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "expression",
    [
        ("1d8mi2"),
        ("1d8ma7"),
        ("1d8e8"),
        ("1d8mi2e8"),
        ("1d8ro1"),
        ("2d8rol1"),
    ],
)
def test_modifiers_single(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)


@pytest.mark.parametrize(
    "expression",
    [
        ("4d6kh2"),
        ("4d6pl2"),
        ("4d6kl2"),
        ("4d6ph2"),
    ],
)
def test_modifiers_multi(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)
