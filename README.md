# d20distribution

Dice rolling distribution calculator based on [d20](https://pypi.org/project/d20/) syntax. Given a valid expression, it calculates the odds of each possible result value being rolled.

## How to use

A distribution can be created using the `parse` function. This returns an object with all the possible values. Each value is a possible dice result. All values have an equal chance of appearing, and a value can appear multiple times.

Alternatively, the distribution can be converted to a dictionary using the `to_dict` method, where he keys are the possible values and the values are the odds of that value being rolled within range [0, 1].

```Python
import d20distribution

distribution = d20distribution.parse("1d8 + 4")
print(distribution.values) # [5, 6, 7, 8, 9, 10, 11, 12]

distribution = distribution.to_dict()
print(distribution) # {5: 0.125, 7: 0.125, ...}
```

## Unsupported Syntax

All valid [d20](https://pypi.org/project/d20/) expressions are supported, except for the following dice modifiers: `rr`, `ro`, `ra`, `e`. These will hopefully be added in the future.
