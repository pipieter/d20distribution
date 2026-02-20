import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from d20distribution import parse


@pytest.mark.parametrize(
    "expression",
    [
        ("14d6mi2"),
        ("13d6mi2"),
        ("12d6mi2"),
        ("11d6mi2"),
        ("10d6mi2"),
        ("9d6mi2"),
        ("8d6mi2"),
    ],
)
def test_mi_fireball(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)


@pytest.mark.parametrize(
    "expression",
    [
        ("14d6"),
        ("13d6"),
        ("12d6"),
        ("11d6"),
        ("10d6"),
        ("9d6"),
        ("8d6"),
    ],
)
def test_fireball(benchmark: BenchmarkFixture, expression: str):
    benchmark(parse, expression)
