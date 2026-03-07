from test import approx, assert_distribution

import pytest

from d20distribution import parse
from d20distribution.errors import DiceParseError, InvalidOperationError


def test_mi():
    distribution = parse("1d6mi3")

    # Verified using anydice.com
    values = [
        (3, 0.5000),
        (4, 0.1667),
        (5, 0.1667),
        (6, 0.1667),
    ]

    assert_distribution(distribution, values)


def test_modifiers_kh():
    distribution = parse("4d6kh2")

    # Verified using anydice.com
    values = [
        (2, 0.0008),
        (3, 0.0031),
        (4, 0.0116),
        (5, 0.0247),
        (6, 0.0502),
        (7, 0.0833),
        (8, 0.1319),
        (9, 0.1728),
        (10, 0.2014),
        (11, 0.1883),
        (12, 0.1319),
    ]

    assert_distribution(distribution, values)


def test_modifiers_pl():
    # Equivalent to kh2
    distribution = parse("4d6pl2")

    # Verified using anydice.com
    values = [
        (2, 0.0008),
        (3, 0.0031),
        (4, 0.0116),
        (5, 0.0247),
        (6, 0.0502),
        (7, 0.0833),
        (8, 0.1319),
        (9, 0.1728),
        (10, 0.2014),
        (11, 0.1883),
        (12, 0.1319),
    ]

    assert_distribution(distribution, values)


def test_modifiers_kl():
    distribution = parse("4d6kl2")

    # Verified using anydice.com
    values = [
        (2, 0.1319),
        (3, 0.1883),
        (4, 0.2014),
        (5, 0.1728),
        (6, 0.1319),
        (7, 0.0833),
        (8, 0.0502),
        (9, 0.0247),
        (10, 0.0116),
        (11, 0.0031),
        (12, 0.0008),
    ]

    assert_distribution(distribution, values)


def test_modifiers_ph():
    distribution = parse("4d6ph2")

    # Verified using anydice.com
    values = [
        (2, 0.1319),
        (3, 0.1883),
        (4, 0.2014),
        (5, 0.1728),
        (6, 0.1319),
        (7, 0.0833),
        (8, 0.0502),
        (9, 0.0247),
        (10, 0.0116),
        (11, 0.0031),
        (12, 0.0008),
    ]

    assert_distribution(distribution, values)


def test_ro_1d4ro1():
    distribution = parse("1d4ro1")

    values = [(1, 0.0625), (2, 0.3125), (3, 0.3125), (4, 0.3125)]

    assert_distribution(distribution, values)


def test_ro_1d6lt4():
    distribution = parse("1d6ro<4")

    values = [
        (1, 0.08333),
        (2, 0.08333),
        (3, 0.08333),
        (4, 0.25000),
        (5, 0.25000),
        (6, 0.25000),
    ]

    assert_distribution(distribution, values)


def test_ro_2d12lo1():
    distribution = parse("2d12rol1")

    # Verified using anydice.com
    values = [
        (2, 0.0006),
        (3, 0.0023),
        (4, 0.0052),
        (5, 0.0093),
        (6, 0.0145),
        (7, 0.0208),
        (8, 0.0284),
        (9, 0.0370),
        (10, 0.0469),
        (11, 0.0579),
        (12, 0.0700),
        (13, 0.0833),
        (14, 0.0828),
        (15, 0.0810),
        (16, 0.0781),
        (17, 0.0741),
        (18, 0.0689),
        (19, 0.0625),
        (20, 0.0550),
        (21, 0.0463),
        (22, 0.0365),
        (23, 0.0255),
        (24, 0.0133),
    ]

    assert_distribution(distribution, values)


def test_e():
    sides = 8
    distribution = parse(f"1d{sides}e8")
    base_chance = 1 / sides
    for roll in distribution.keys():
        depth = (roll - 1) // sides + 1
        expected = base_chance**depth
        actual = distribution.get(roll)
        assert expected == approx(actual)


def test_e_2():
    distribution = parse("1d8e8")

    # Verified using anydice.com
    # output [explode 1d8]
    values = [
        (1, 0.125),
        (2, 0.125),
        (3, 0.125),
        (4, 0.125),
        (5, 0.125),
        (6, 0.125),
        (7, 0.125),
        (9, 0.015625),
        (10, 0.015625),
        (11, 0.015625),
        (12, 0.015625),
        (13, 0.015625),
        (14, 0.015625),
        (15, 0.015625),
        (17, 0.001953125),
        (18, 0.001953125),
        (19, 0.001953125),
        (20, 0.001953125),
        (21, 0.001953125),
        (22, 0.001953125),
        (23, 0.001953125),
        # On anydice, 24 is the summation of all values of 24 and beyond,
        # as they have a limit on rounding
        (24, 0.001953125),
    ]

    assert_distribution(distribution, values[:-1])

    last_roll = values[-1][0]
    expected = values[-1][1]
    actual = distribution.get_at_least(last_roll)
    assert expected == approx(actual)


def test_e_3():
    distribution = parse("1d10mi5e10")

    # Verified using anydice.com
    # output [explode [highest of 1d10 and 5]]
    values = [
        (5, 0.50),
        (6, 0.10),
        (7, 0.10),
        (8, 0.10),
        (9, 0.10),
        (15, 0.05),
        (16, 0.01),
        (17, 0.01),
        (18, 0.01),
        (19, 0.01),
        (25, 0.005),
        (26, 0.001),
        (27, 0.001),
        (28, 0.001),
        (29, 0.001),
        (30, 0.001),
    ]

    assert_distribution(distribution, values[:-1])

    last_roll = values[-1][0]
    expected = values[-1][1]
    actual = distribution.get_at_least(last_roll)
    assert expected == approx(actual)


def test_e_gt():
    # anydice.com can't generate accurate test data for this, thus we do an estimate test to see that the base is correct.
    sides = 8
    threshold = 4
    distribution = parse(f"1d{sides}e>{threshold}")
    base_odds = 1 / sides

    for i in range(1, threshold):
        actual = distribution.get(i)
        expected = base_odds
        assert expected == approx(actual), f"Result {i} should stay at base odds ({base_odds}), but was {actual}."

    gap_value = threshold + 1
    actual_gap = distribution.get(gap_value)
    msg = f"Result {gap_value} should be impossible (0%) as it's the 'gap' after an explosion, but was {actual_gap}."
    assert distribution.get(threshold + 1) == approx(0), msg

    for i in range(1, sides - threshold):
        value = threshold + 1 + i
        actual = distribution.get(value)
        expected = base_odds * base_odds * i
        msg = f"Result {value} odds incorrect: Expected {expected} ({base_odds}^2 * {i}), but was {actual}."
        assert expected == approx(actual), msg


def test_e_lt():
    # anydice.com can't generate accurate test data for this, thus we do an estimate test to see that the base is correct.
    sides = 8
    threshold = 4
    distribution = parse(f"1d{sides}e<{threshold}")

    base_odds = 1 / sides
    for i in range(1, threshold - 1):
        actual = distribution.get(i)
        assert actual == approx(0), f"Result {i} should be impossible (0%) because it triggers an explosion, but got {actual}."

    actual_threshold_odds = distribution.get(threshold)
    msg = f"Result {threshold} (the threshold) should remain at base odds ({base_odds}), but was {actual_threshold_odds}."
    assert actual_threshold_odds == approx(base_odds), msg

    for i in range(threshold + 1, sides):
        actual = distribution.get(i)
        msg = f"Result {i} should have boosted odds (> {base_odds}) due to explosion sums, but was {actual}."
        assert actual > base_odds, msg


def test_ra_1d6():
    distribution = parse("1d6ra6")

    # Verified using anydice.com
    # set "explode depth" to 1
    # output [explode 1d6]

    values = [
        (1, 0.166666666667),
        (2, 0.166666666667),
        (3, 0.166666666667),
        (4, 0.166666666667),
        (5, 0.166666666667),
        (7, 0.0277777777778),
        (8, 0.0277777777778),
        (9, 0.0277777777778),
        (10, 0.0277777777778),
        (11, 0.0277777777778),
        (12, 0.0277777777778),
    ]

    assert_distribution(distribution, values)


def test_ra_4d6_low():
    distribution = parse("2d6ra<4")

    # Verified using anydice.com
    #
    # function: reroll and add A:s on less than N:n with B:s {
    #   if (A < N) > 0 { result: A + B}
    #   result: A
    # }
    # output [reroll and add 2d6 on less than 4 with 1d6]

    values = [
        (3, 0.00462962962963),
        (4, 0.0138888888889),
        (5, 0.0277777777778),
        (6, 0.0462962962963),
        (7, 0.0694444444444),
        (8, 0.1250000000000),
        (9, 0.166666666667),
        (10, 0.194444444444),
        (11, 0.152777777778),
        (12, 0.106481481481),
        (13, 0.0555555555556),
        (14, 0.0277777777778),
        (15, 0.00925925925926),
    ]

    assert_distribution(distribution, values)


def test_rr_1():
    distribution = parse("1d6rr1")

    # This should be equivalent to 1d5+1
    values = [
        (2, 0.2),
        (3, 0.2),
        (4, 0.2),
        (5, 0.2),
        (6, 0.2),
    ]

    assert_distribution(distribution, values)


def test_rr_lt5():
    distribution = parse("1d6rr<5")

    # This should be equivalent to 1d2+4
    values = [
        (5, 0.5),
        (6, 0.5),
    ]

    assert_distribution(distribution, values)


def test_rr_equal():
    distribution = parse("2d6mi6rr>4")

    # Verified using anydice.com
    # all dice will be re-rolled, and the new dice will be equivalent to 2d4
    values = [
        (2, 0.0625),
        (3, 0.1250),
        (4, 0.1875),
        (5, 0.2500),
        (6, 0.1875),
        (7, 0.1250),
        (8, 0.0625),
    ]

    assert_distribution(distribution, values)


@pytest.mark.parametrize(
    "infinite, expression",
    [
        (True, "1d6rr<7"),
        (True, "1d6rr>0"),
        (True, "1d6rrl1"),
        (True, "1d6rrh4"),
        (True, "1d1rr1"),
        (True, "1d6rrl0"),
        (True, "1d6rrh0"),
        (False, "1d6rr1"),
        (False, "1d6rr<6"),
        (False, "1d6rr>1"),
    ],
)
def test_rr_infinite_loops(infinite: bool, expression: str):
    if infinite:
        with pytest.raises((InvalidOperationError, DiceParseError)):
            parse(expression)
    else:
        parse(expression)


def test_chain():
    distribution = parse("2d12rol1mi3")

    # Verified using anydice.com
    values = [
        (6, 0.0156),
        (7, 0.0174),
        (8, 0.0249),
        (9, 0.0336),
        (10, 0.0434),
        (11, 0.0544),
        (12, 0.0666),
        (13, 0.0799),
        (14, 0.0943),
        (15, 0.1100),
        (16, 0.0781),
        (17, 0.0741),
        (18, 0.0689),
        (19, 0.0625),
        (20, 0.0550),
        (21, 0.0463),
        (22, 0.0365),
        (23, 0.0255),
        (24, 0.0133),
    ]

    assert_distribution(distribution, values)


def test_mi_out_of_bounds():
    distribution = parse("1d20mi21")

    assert distribution.get(21) == approx(1.0)
    assert distribution.mean() == approx(21.0)
    assert distribution.stdev() == approx(0.0)


def test_valid_operations():
    """
    This test is meant to be used to ensure that specific scenarios are running
    correctly, i.e. they do not throw any errors during the calculations. They
    are mainly used to test combining modifiers
    """

    parse("4d6kh3rol2")
