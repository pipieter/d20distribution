import abc
from collections import defaultdict

import d20  # type: ignore

from .distribution import Distribution

class AbstractDistributionBuilder(abc.ABC):
    """An abstract class used to build distributions."""

    @abc.abstractmethod
    def distribution(self) -> Distribution:
        """Build the distribution based on the builder.

        Returns:
            Distribution: The distribution object matching the current state of the distribution.
        """
        ...

    def apply_operation(self, op: d20.ast.Operator) -> None:
        """Apply a valid d20 operator to the current distribution. This internally  changes the
        state of the builder

        Args:
            op (d20.ast.Operator): The operator to be applied.

        Raises:
            InvalidOperationError: When the operation in question is unknown or not supported.
        """
        ...

    @abc.abstractmethod
    def apply_mi(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 minimum operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `mi` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ma(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 maximum operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `ma` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ro(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 re-roll once operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `ro` operator.
        """
        ...

    @abc.abstractmethod
    def apply_e(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 explode operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `e` operator.
        """
        ...

    @abc.abstractmethod
    def apply_k(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 keep operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `k` operator.
        """
        ...

    @abc.abstractmethod
    def apply_p(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 drop operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `p` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ra(self, selectors: list[d20.ast.Selector]) -> None:
        """Apply the d20 reroll and add operator to the builder.

        Args:
            selectors (list[d20.ast.Selector]): A list of valid d20 selectors matching the `ra` operator.
        """
        ...

class ConvolutionDistributionBuilder(AbstractDistributionBuilder):
    """
    A distribution builder that internally uses convolutions to calculate the distribution.
    These convolutions are typically much faster than iterating over all possibilities, but
    they are more limited in the operations they can perform.

    For more information on how convolutions work, see this blog post:
    https://blog.demofox.org/2025/01/05/dice-deconvolution-and-generating-functions/


    Raises:
        InvalidOperationError: When an invalid operator is passed as an argument. Certain operations are not possible using convolutions.
    """

    _count: int
    _sides: int
    _convolution: list[float]
    def __init__(self, count: int, sides: int, operations: list[d20.ast.Operator]) -> None:
        """Create a convolution distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[d20.ast.Operator]): A list of operators to be applied to the expression.
        """
        ...

    def distribution(self) -> Distribution: ...
    @staticmethod
    def supports_operation(operation: d20.ast.Operator) -> bool:
        """Checks if the ConvolutionDistributionBuilder supports an operation.

        Args:
            operation (d20.ast.Operator): The operation to be checked.

        Returns:
            bool: Whether the operation is supported.
        """
        ...

    def apply_mi(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ma(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_k(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_p(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ro(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_e(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ra(self, selectors: list[d20.ast.Selector]) -> None: ...

DiscreteKey = tuple[int, ...]

class DiscreteDistributionBuilder(AbstractDistributionBuilder):
    _count: int
    _sides: int
    _dist: defaultdict[DiscreteKey, float]
    def __init__(self, count: int, sides: int, operations: list[d20.ast.Operator]) -> None:
        """Create a discrete distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[d20.ast.Operator]): A list of operators to be applied to the expression.
        """
        ...

    def distribution(self) -> Distribution: ...
    def apply_mi(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ma(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_k(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_p(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ro(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_e(self, selectors: list[d20.ast.Selector]) -> None: ...
    def apply_ra(self, selectors: list[d20.ast.Selector]) -> None: ...
