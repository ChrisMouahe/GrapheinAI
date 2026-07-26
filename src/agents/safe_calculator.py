"""Safe Calculator implementing strict AST parsing and evaluation with Anti-DoS protection.

Exclusively permits basic mathematical operators (+, -, *, /, //, %, **) and numerical values.
Forbids function calls, attribute accesses, variable lookups, imports, eval, exec, and arbitrary code execution.
Incorporates strict length limits and exponent bounds to prevent Math Bomb / CPU exhaustion attacks.
"""

import ast
import operator
from typing import Callable, Union

from src.models.exceptions import (
    DivisionByZeroCalcError,
    ForbiddenASTNodeError,
    InvalidExpressionError,
    SafeCalculatorError,
)

Numeric = Union[int, float]


class SafeCalculator:
    """AST-based arithmetic evaluator guaranteeing secure computation."""

    ALLOWED_BIN_OPS: dict[type[ast.operator], Callable[[Numeric, Numeric], Numeric]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    ALLOWED_UNARY_OPS: dict[type[ast.unaryop], Callable[[Numeric], Numeric]] = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(self, expression: str) -> Numeric:
        """Safely evaluates an arithmetic expression using AST inspection."""
        if not expression or not expression.strip():
            raise InvalidExpressionError("Expression cannot be empty.")

        # SÉCURITÉ 1 : Limite stricte de longueur (Anti-Stack Overflow & Nombres géants)
        if len(expression) > 250:
            raise InvalidExpressionError("L'expression dépasse la longueur maximale autorisée de 250 caractères.")

        try:
            parsed_ast = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as e:
            raise InvalidExpressionError(f"Syntax error in expression: {e}") from e

        return self._eval_node(parsed_ast)

    def validate_expression(self, expression: str) -> bool:
        """Checks whether an expression is syntactically valid and secure without raising errors."""
        try:
            self.evaluate(expression)
            return True
        except SafeCalculatorError:
            return False

    def _eval_node(self, node: ast.AST) -> Numeric:
        """Recursively evaluates an AST node with strict whitelist checking."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ForbiddenASTNodeError(
                    "Boolean", "Boolean constants are forbidden in SafeCalculator."
                )
            if isinstance(node.value, (int, float)):
                return node.value
            raise ForbiddenASTNodeError(
                type(node.value).__name__,
                f"Constant of type '{type(node.value).__name__}' is forbidden.",
            )

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_BIN_OPS:
                raise ForbiddenASTNodeError(op_type.__name__)

            left_val = self._eval_node(node.left)
            right_val = self._eval_node(node.right)

            # SÉCURITÉ 2 : Prévention des "Math Bombs" (Limitation stricte des exposants)
            if op_type == ast.Pow:
                if abs(left_val) > 10000 or abs(right_val) > 100:
                    raise SafeCalculatorError("Calcul exponentiel bloqué : Valeurs trop grandes (Sécurité Anti-DoS).")

            # Check for division/modulo by zero
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
                raise DivisionByZeroCalcError("Division or modulo by zero is not allowed.")

            return self.ALLOWED_BIN_OPS[op_type](left_val, right_val)

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_UNARY_OPS:
                raise ForbiddenASTNodeError(op_type.__name__)

            operand_val = self._eval_node(node.operand)
            return self.ALLOWED_UNARY_OPS[op_type](operand_val)

        node_name = type(node).__name__
        raise ForbiddenASTNodeError(
            node_name, f"Unauthorized AST node '{node_name}' detected in expression."
        )