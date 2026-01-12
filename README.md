# d20distribution

Dice rolling distribution calculator based on [d20](https://pypi.org/project/d20/) syntax. Given a valid expression, it calculates the odds of each possible result value being rolled.

## How to use

A distribution can be created using the `parse` function. This returns an object with all the possible values. Each value is a possible dice result. All values have an equal chance of appearing, and a value can appear multiple times.

The possible values can be found with `.keys()`. Individual values can be retrieved with `.get()`. The mean and standard deviation can be found with `.mean()` and `.stdev()` respectively.

```Python
import d20distribution

distribution = d20distribution.parse("1d8 + 4")
print(distribution.get(5)) # 0.125
print(distribution.mean()) # 8.50
```

## Unsupported Syntax

All valid [d20](https://pypi.org/project/d20/) expressions are supported, except for the following dice modifiers: `rr` and `ra`. These will hopefully be added in the future.
