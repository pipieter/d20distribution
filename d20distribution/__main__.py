import os
import time

try:
    import readline  # type: ignore # Allows for users to navigate previous inputs on certain systems
except:
    ...

from .parser import parse
from .distribution import DiceDistribution


def print_distribution(dist: DiceDistribution, line_width: int) -> None:
    keys = dist.keys()
    values = dist.dist.values()

    if any(not isinstance(key, int) for key in keys):  # type: ignore # specific case in expression like 0.5 * 1d8, where the values are converted to floats
        raise ValueError("Distribution contains non-integer keys, and cannot be visualized.")

    min_key = min(keys)
    max_key = max(keys)
    max_value = max(values)
    key_lengths = [len(str(key)) for key in keys]
    value_lengths = [len(f"{100 * value:.3f}") for value in values]

    key_print_width = max(key_lengths)
    value_print_width = max(value_lengths)

    def format_entry(key: int, value: float) -> str:
        key_str = str(key)
        val_str = f"{(100*value):.3f}"
        return f"{key_str.rjust(key_print_width)}.  {val_str.rjust(value_print_width)}%"

    total_width_for_bars = line_width - len(format_entry(max(key_lengths), max(value_lengths))) - 2

    # Only print the bars if sufficient space
    print_chart_bars = total_width_for_bars >= 10
    white_square = "\u2588"

    for key in range(min_key, max_key + 1):
        value = dist.get(key)

        number_of_bars = 0
        if print_chart_bars:
            number_of_bars = int(total_width_for_bars * value / max_value)
        bars = number_of_bars * white_square

        print(f"{format_entry(key, value)}  {bars}")


if __name__ == "__main__":
    quit_words = ["exit", "quit", "stop", "halt"]
    max_width = 64

    while True:
        try:
            expr = input("> ")

            if expr.lower() in quit_words:
                break

            timer_start = time.time()
            dist = parse(expression=expr)
            timer_end = time.time()

            mean = f"{dist.mean():.2f}"
            stdev = f"{dist.stdev():.2f}"
            duration = timer_end - timer_start
            mean_padding = max(len(mean), len(stdev))

            print(f"Calculation time: {duration:.2f} seconds")
            print(f"Mean:  {mean.rjust(mean_padding)}")
            print(f"Stdev: {stdev.rjust(mean_padding)}")
            print()

            line_width = min(os.get_terminal_size().columns, max_width)
            print_distribution(dist, line_width)

        # Graciously exit on CTRL+C
        except KeyboardInterrupt:
            print()
            break

        # Graciously exit on CTRL+D
        except EOFError:
            print()
            break

        except Exception as e:
            print(f"Error: {str(e)}")

        print()
