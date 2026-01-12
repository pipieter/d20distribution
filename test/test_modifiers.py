import pytest
from d20distribution import parse
from d20distribution.errors import InvalidOperationError


def equal(a: float, b: float, epsilon=1e-6) -> bool:
    return abs(a - b) <= epsilon


def test_mi():
    distribution = parse("1d6mi3")

    # Odds based on anydice.com
    odds = [
        (3, 50.00),
        (4, 16.67),
        (5, 16.67),
        (6, 16.67),
    ]
    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_modifiers_kh():
    distribution = parse("4d6kh2")

    # Odds based on anydice.com
    odds = [
        (2, 0.08),
        (3, 0.31),
        (4, 1.16),
        (5, 2.47),
        (6, 5.02),
        (7, 8.33),
        (8, 13.19),
        (9, 17.28),
        (10, 20.14),
        (11, 18.83),
        (12, 13.19),
    ]
    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_modifiers_pl():
    # Equivalent to kh2
    distribution = parse("4d6pl2")

    # Odds based on anydice.com
    odds = [
        (2, 0.08),
        (3, 0.31),
        (4, 1.16),
        (5, 2.47),
        (6, 5.02),
        (7, 8.33),
        (8, 13.19),
        (9, 17.28),
        (10, 20.14),
        (11, 18.83),
        (12, 13.19),
    ]
    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_modifiers_kl():
    distribution = parse("4d6kl2")

    # Odds based on anydice.com
    odds = [
        (2, 13.19),
        (3, 18.83),
        (4, 20.14),
        (5, 17.28),
        (6, 13.19),
        (7, 8.33),
        (8, 5.02),
        (9, 2.47),
        (10, 1.16),
        (11, 0.31),
        (12, 0.08),
    ]
    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_modifiers_ph():
    distribution = parse("4d6ph2")

    # Odds based on anydice.com
    odds = [
        (2, 13.19),
        (3, 18.83),
        (4, 20.14),
        (5, 17.28),
        (6, 13.19),
        (7, 8.33),
        (8, 5.02),
        (9, 2.47),
        (10, 1.16),
        (11, 0.31),
        (12, 0.08),
    ]
    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_modifiers_rr_unsupported():
    # rr is currently unsupported
    with pytest.raises(InvalidOperationError):
        parse("1d20rr1")


def test_ro_1():
    distribution = parse("1d4ro1")

    odds = [(1, 0.0625), (2, 0.3125), (3, 0.3125), (4, 0.3125)]

    for value, chance in odds:
        assert equal(chance, distribution.get(value), 0.0001)


def test_ro_2():
    distribution = parse("2d12rol1")

    # Odds based on anydice.com
    odds = [
        (2, 0.06),
        (3, 0.23),
        (4, 0.52),
        (5, 0.93),
        (6, 1.45),
        (7, 2.08),
        (8, 2.84),
        (9, 3.70),
        (10, 4.69),
        (11, 5.79),
        (12, 7.00),
        (13, 8.33),
        (14, 8.28),
        (15, 8.10),
        (16, 7.81),
        (17, 7.41),
        (18, 6.89),
        (19, 6.25),
        (20, 5.50),
        (21, 4.63),
        (22, 3.65),
        (23, 2.55),
        (24, 1.33),
    ]

    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)


def test_e():
    sides = 8
    distribution = parse(f"1d{sides}e8")
    base_chance = 1 / sides
    for value in distribution.keys():
        depth = (value - 1) // sides + 1
        chance = base_chance**depth

        assert abs(chance - distribution.get(value)) < 1e-7


def test_e_2():
    distribution = parse("1d8e8")

    # Odds based on anydice.com
    # output [explode 1d8]
    odds = [
        (1, 12.5),
        (2, 12.5),
        (3, 12.5),
        (4, 12.5),
        (5, 12.5),
        (6, 12.5),
        (7, 12.5),
        (9, 1.5625),
        (10, 1.5625),
        (11, 1.5625),
        (12, 1.5625),
        (13, 1.5625),
        (14, 1.5625),
        (15, 1.5625),
        (17, 0.1953125),
        (18, 0.1953125),
        (19, 0.1953125),
        (20, 0.1953125),
        (21, 0.1953125),
        (22, 0.1953125),
        (23, 0.1953125),
        # On anydice, 24 is the summation of all values of 24 and beyond,
        # as they have a limit on rounding
        (24, 0.1953125),
    ]

    for value, chance in odds[:-1]:
        assert equal(chance, 100 * distribution.get(value), 0.001)

    assert equal(odds[-1][1], 100 * distribution.get_at_least(odds[-1][0]), 0.001)


def test_e_3():
    distribution = parse("1d10mi5e10")

    # Odds based on anydice.com
    # output [explode [highest of 1d10 and 5]]
    odds = [
        (5, 50),
        (6, 10),
        (7, 10),
        (8, 10),
        (9, 10),
        (15, 5),
        (16, 1),
        (17, 1),
        (18, 1),
        (19, 1),
        (25, 0.5),
        (26, 0.1),
        (27, 0.1),
        (28, 0.1),
        (29, 0.1),
        (30, 0.1),
    ]

    for value, chance in odds[:-1]:
        assert equal(chance, 100 * distribution.get(value), 0.001)

    assert equal(odds[-1][1], 100 * distribution.get_at_least(odds[-1][0]), 0.001)


def test_chain():
    distribution = parse("2d12rol1mi3")

    # Odds based on anydice.com
    odds = [
        (6, 1.56),
        (7, 1.74),
        (8, 2.49),
        (9, 3.36),
        (10, 4.34),
        (11, 5.44),
        (12, 6.66),
        (13, 7.99),
        (14, 9.43),
        (15, 11.00),
        (16, 7.81),
        (17, 7.41),
        (18, 6.89),
        (19, 6.25),
        (20, 5.50),
        (21, 4.63),
        (22, 3.65),
        (23, 2.55),
        (24, 1.33),
    ]

    for value, chance in odds:
        assert equal(chance, 100 * distribution.get(value), 0.01)
