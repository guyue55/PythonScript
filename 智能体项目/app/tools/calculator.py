"""安全计算器工具。

提供对基础算术表达式的安全计算，避免使用不安全的 `eval`。
支持的运算：加、减、乘、除、整除、取模、幂，以及括号。
"""

from __future__ import annotations

import ast
import operator
from typing import Any


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


def _eval_node(node: ast.AST) -> Any:
    """递归安全求值 AST 节点。

    Args:
        node: AST 节点。

    Returns:
        Any: 计算结果（通常为数值）。

    Raises:
        ValueError: 当出现不支持的语法时抛出。
    """

    if isinstance(node, ast.Num):  # Py<3.8
        return node.n
    if isinstance(node, ast.Constant):  # Py>=3.8
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("仅支持数字常量。")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type in _OPS:
            return _OPS[op_type](left, right)
        raise ValueError("不支持的运算符。")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _eval_node(node.operand)
        return +operand if isinstance(node.op, ast.UAdd) else -operand
    if isinstance(node, ast.Expr):
        return _eval_node(node.value)
    raise ValueError("不支持的表达式结构。")


def safe_calculate(expression: str) -> float:
    """安全计算基础算术表达式。

    Args:
        expression: 算术表达式字符串，例如 "(2+3)*4/5"。

    Returns:
        float: 计算结果（浮点）。
    """

    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree.body)
    return float(result)