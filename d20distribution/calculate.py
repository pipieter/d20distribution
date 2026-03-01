import abc

import d20  # type: ignore
import numpy as np

from .distribution import DiceDistribution
from .errors import InvalidOperationError


class AbstractDistributionBuilder(abc.ABC):
    @abc.abstractmethod
    def distribution(self) -> DiceDistribution: ...

    def apply_operation(self, op: d20.SetOperator) -> None:
        operation_functions = {
            "mi": self.apply_mi,
            "ma": self.apply_ma,
            "ro": self.apply_ro,
            "e": self.apply_e,
            "k": self.apply_k,
            "p": self.apply_p,
            # Unimplemented operations
            # "rr": self.apply_rr,
            # "ra": self.apply_ra,
        }

        operation: str = op.op
        selectors: list[d20.SetSelector] = op.sels

        if operation not in operation_functions:
            raise InvalidOperationError(f"Unsupported operator: '{op.op}'")

        operation_functions[operation](selectors)

    @abc.abstractmethod
    def apply_mi(self, selectors: list[d20.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_ma(self, selectors: list[d20.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_ro(self, selectors: list[d20.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_e(self, selectors: list[d20.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_k(self, selectors: list[d20.SetSelector]) -> None: ...

    @abc.abstractmethod
    def apply_p(self, selectors: list[d20.SetSelector]) -> None: ...


class ConvolutionDistributionBuilder(AbstractDistributionBuilder):
    count: int
    sides: int
    convolution: list[float]

    def __init__(self, count: int, sides: int, operations: list[d20.SetOperator]) -> None:
        super().__init__()
        self.count = count
        self.sides = sides
        self.convolution = [0] + [1 / sides] * sides

        for operation in operations:
            self.apply_operation(operation)

    def distribution(self) -> DiceDistribution:
        result = np.array([1.0])
        convolution = np.array(self.convolution)
        for _ in range(self.count):
            result = np.convolve(result, convolution)

        dist = {k: float(v) for k, v in enumerate(result) if abs(v) >= 1e-10}
        return DiceDistribution(dist)

    @staticmethod
    def supports_operation(operation: d20.SetOperator) -> bool:
        invalid_operations = ["e", "ra"]
        invalid_selector_categories = ["h", "l"]

        if operation.op in invalid_operations:
            return False

        categories: list[str] = [sel.cat for sel in operation.sels]  # type: ignore
        if any(category in invalid_selector_categories for category in categories):
            return False

        return True

    @staticmethod
    def _matches_selector(value: int, selector: d20.SetSelector) -> bool:
        cat: str | None = selector.cat

        if cat in ["", None]:
            return value == selector.num

        if cat == "<":
            return value < selector.num

        if cat == ">":
            return value > selector.num

        raise InvalidOperationError(f"Invalid operation found between value '{value}' and '{cat}'")

    def apply_mi(self, selectors: list[d20.SetSelector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for mi: '{selector.cat}'")

            num: int = selector.num

            # Extend the convolution
            padding = num - len(self.convolution) + 1
            self.convolution.extend([0] * padding)
            for i in range(1, num):
                self.convolution[num] += self.convolution[i]
                self.convolution[i] = 0

    def apply_ma(self, selectors: list[d20.SetSelector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise InvalidOperationError(f"Unsupported selector category for ma: '{selector.cat}'")

            num: int = selector.num
            for i in range(num + 1, len(self.convolution)):
                self.convolution[num] += self.convolution[i]
                self.convolution[i] = 0

    def apply_k(self, selectors: list[d20.SetSelector]) -> None:
        for selector in selectors:
            for i in range(1, len(self.convolution)):
                if not self._matches_selector(i, selector):
                    self.convolution[0] += self.convolution[i]
                    self.convolution[i] = 0

    def apply_p(self, selectors: list[d20.SetSelector]) -> None:
        for selector in selectors:
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    self.convolution[0] += self.convolution[i]
                    self.convolution[i] = 0

    def apply_ro(self, selectors: list[d20.SetSelector]) -> None:
        for selector in selectors:
            reroll = 1 / self.sides
            odds_occurring = 0
            odds_not_occurring = 0
            sides_not_occurring = 0

            # Calculate the odds of event occuring
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    odds_occurring += self.convolution[i]
                else:
                    odds_not_occurring += self.convolution[i]
                    sides_not_occurring += 1

            # Re-calculate the odds
            for i in range(1, len(self.convolution)):
                if self._matches_selector(i, selector):
                    self.convolution[i] = odds_occurring * reroll
                else:
                    self.convolution[i] += odds_not_occurring * reroll / sides_not_occurring

    def apply_e(self, selectors: list[d20.SetSelector]) -> None:
        raise InvalidOperationError(f"Explode operator not supported fro ConvolutionDistributionBuilder")
