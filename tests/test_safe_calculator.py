"""Comprehensive test suite for SafeCalculator verifying correctness and security guarantees."""

import pytest

from src.agents.safe_calculator import SafeCalculator
from src.models.exceptions import (
    DivisionByZeroCalcError,
    ForbiddenASTNodeError,
    InvalidExpressionError,
)


@pytest.fixture
def calc() -> SafeCalculator:
    return SafeCalculator()


class TestSafeCalculatorArithmetic:
    """Tests for allowed arithmetic expressions."""

    def test_additions(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("1 + 1") == 2
        assert calc.evaluate("10 + 20 + 30") == 60
        assert calc.evaluate("0 + 0") == 0
        assert calc.evaluate("3.5 + 2.5") == 6.0

    def test_subtractions(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("10 - 4") == 6
        assert calc.evaluate("5 - 15") == -10
        assert calc.evaluate("100 - 50 - 25") == 25
        assert calc.evaluate("7.8 - 2.3") == pytest.approx(5.5)

    def test_multiplications(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("3 * 4") == 12
        assert calc.evaluate("0 * 100") == 0
        assert calc.evaluate("2.5 * 4") == 10.0
        assert calc.evaluate("2 * 3 * 4") == 24

    def test_divisions(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("10 / 2") == 5.0
        assert calc.evaluate("7 / 2") == 3.5
        assert calc.evaluate("15 // 4") == 3
        assert calc.evaluate("10 % 3") == 1

    def test_powers(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("2 ** 3") == 8
        assert calc.evaluate("3 ** 2") == 9

    def test_parentheses(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("(2 + 3) * 4") == 20
        assert calc.evaluate("2 + (3 * 4)") == 14
        assert calc.evaluate("((10 - 2) * (3 + 1)) / 4") == 8.0

    def test_negative_numbers(self, calc: SafeCalculator) -> None:
        assert calc.evaluate("-5") == -5
        assert calc.evaluate("+5") == 5
        assert calc.evaluate("-5 + 10") == 5
        assert calc.evaluate("10 + -3") == 7
        assert calc.evaluate("-(4 + 6)") == -10
        assert calc.evaluate("-3 * -4") == 12

    def test_validate_expression(self, calc: SafeCalculator) -> None:
        assert calc.validate_expression("10 + 20") is True
        assert calc.validate_expression("import os") is False
        assert calc.validate_expression("invalid syntax ++") is False


class TestSafeCalculatorSecurityAndInjections:
    """Tests verifying that malicious code, injections, calls, and attributes are rejected."""

    def test_division_by_zero(self, calc: SafeCalculator) -> None:
        with pytest.raises(DivisionByZeroCalcError):
            calc.evaluate("10 / 0")

        with pytest.raises(DivisionByZeroCalcError):
            calc.evaluate("10 // 0")

        with pytest.raises(DivisionByZeroCalcError):
            calc.evaluate("10 % 0")

    def test_syntax_errors_and_empty(self, calc: SafeCalculator) -> None:
        with pytest.raises(InvalidExpressionError):
            calc.evaluate("")

        with pytest.raises(InvalidExpressionError):
            calc.evaluate("   ")

        with pytest.raises(InvalidExpressionError):
            calc.evaluate("1 + +")

        with pytest.raises(InvalidExpressionError):
            calc.evaluate("((1 + 2)")

    def test_forbidden_functions(self, calc: SafeCalculator) -> None:
        forbidden_calls = [
            "eval('1+1')",
            "exec('print(1)')",
            "print('hello')",
            "abs(-5)",
            "min(1, 2)",
            "max(3, 4)",
            "open('/etc/passwd')",
        ]
        for expr in forbidden_calls:
            with pytest.raises(ForbiddenASTNodeError) as exc_info:
                calc.evaluate(expr)
            assert "Call" in str(exc_info.value) or "Forbidden" in str(exc_info.value)

    def test_forbidden_imports(self, calc: SafeCalculator) -> None:
        forbidden_imports = [
            "import os",
            "import sys",
            "from math import sqrt",
            "__import__('os').system('ls')",
        ]
        for expr in forbidden_imports:
            with pytest.raises((ForbiddenASTNodeError, InvalidExpressionError)):
                calc.evaluate(expr)

    def test_forbidden_attribute_access(self, calc: SafeCalculator) -> None:
        forbidden_attrs = [
            "(1).__class__",
            "'string'.upper()",
            "__builtins__.__dict__",
            "(10).real",
        ]
        for expr in forbidden_attrs:
            with pytest.raises(ForbiddenASTNodeError):
                calc.evaluate(expr)

    def test_forbidden_variables_and_names(self, calc: SafeCalculator) -> None:
        forbidden_names = [
            "x + 1",
            "foo",
            "__name__",
            "True",
            "False",
            "None",
        ]
        for expr in forbidden_names:
            with pytest.raises(ForbiddenASTNodeError):
                calc.evaluate(expr)

    def test_forbidden_arbitrary_code(self, calc: SafeCalculator) -> None:
        arbitrary_code = [
            "[x for x in range(10)]",
            "{'a': 1}",
            "lambda x: x + 1",
            "1 if True else 0",
            "1 == 1",
            "1 < 2",
        ]
        for expr in arbitrary_code:
            with pytest.raises(ForbiddenASTNodeError):
                calc.evaluate(expr)
