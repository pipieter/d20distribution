from d20distribution.distribution import DiceDistribution


def equal(a: float, b: float, epsilon: float = 1e-6) -> bool:
    return abs(a - b) <= epsilon


def assert_anydice(distribution: DiceDistribution, values: list[tuple[int, float]]) -> None:
    for roll, odds in values:
        assert equal(distribution.get(roll), odds)
