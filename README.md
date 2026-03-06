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

All valid [d20](https://pypi.org/project/d20/) expressions are supported, and it is suggested for the user to check their documentation in detail.

## Performance

Internally, two distribution builders are used depending on the modifiers used. These two distributions use convolutions and discrete keys, respectively. The convolution builder is significantly faster (up to 100x performance for certain expressions), but is also more limited. Depending on which builder is used, performance may change drastically.

More specifically, the discrete key builder is used in the following cases:

- The `e` and `ra` modifiers are used.
- The `h` and `l` selectors are used for any modifier.

Care should thus be taken in these scenarios, as the execution time can exponentially increase with the number of dice and the number of sides the dice have. This library does not utilize any internal limits, and it is up to the user to avoid overly complex expressions.

## Using the library interactively

In order to test the library or to visualize distributions, the library can be used interactively by using the command

```bash
python -m d20distribution
```

This opens up a command prompt for the user where they can input distributions, which will visualize the distribution.
