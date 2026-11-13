"""A closed formula reader. It does not call Excel and it does not guess.

Supported: numbers, cell references, ranges, parentheses, + - * /, and
SUM, AVERAGE, MIN, MAX, and IF. Anything else is named and left unevaluated.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

_TOKEN = re.compile(
    r"""
    (?P<ws>\s+)
    | (?P<string>"(?:[^"]|"")*")
    | (?P<number>\d+(?:\.\d+)?)
    | (?P<cmp><=|>=|<>|<|>|=)
    | (?P<op>[\+\-\*/])
    | (?P<lparen>\()
    | (?P<rparen>\))
    | (?P<comma>,)
    | (?P<colon>:)
    | (?P<ref>(?:(?:'(?:[^']|'')+'|[A-Za-z][A-Za-z0-9_]*)!)?\$?[A-Z]{1,3}\$?\d+)
    | (?P<name>[A-Za-z][A-Za-z0-9_]*)
    | (?P<other>.)
    """,
    re.VERBOSE,
)
_CELL = re.compile(r"^((?:'(?:[^']|'')+'|[A-Za-z][A-Za-z0-9_]*)!)?(\$)?([A-Z]{1,3})(\$)?(\d+)$")
_FUNCTIONS = {"SUM", "AVERAGE", "MIN", "MAX", "IF"}
_SKIP_LITERALS = {Decimal("0"), Decimal("1"), Decimal("-1")}


class FormulaError(Exception):
    """The formula is outside the closed set. The value is not guessed."""


@dataclass(frozen=True)
class Ref:
    sheet: str | None
    col: int
    row: int
    abs_col: bool
    abs_row: bool

    def address(self, origin_sheet: str) -> str:
        sheet = self.sheet or origin_sheet
        return f"{sheet}!{_col_name(self.col)}{self.row}"


@dataclass(frozen=True)
class Num:
    value: Decimal


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Bin:
    op: str
    left: Any
    right: Any


@dataclass(frozen=True)
class Unary:
    expr: Any


@dataclass(frozen=True)
class Cmp:
    op: str
    left: Any
    right: Any


@dataclass(frozen=True)
class Call:
    name: str
    args: tuple


@dataclass(frozen=True)
class Range:
    start: Ref
    end: Ref


@dataclass
class Parsed:
    tree: Any
    literals: list[str]
    r1c1: str


def _col_index(letters: str) -> int:
    number = 0
    for character in letters:
        number = number * 26 + (ord(character) - 64)
    return number


def _col_name(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def parse_address(address: str) -> tuple[str, str]:
    sheet, separator, cell = address.partition("!")
    if not separator:
        raise FormulaError("a cell address needs a sheet")
    return sheet, cell.upper()


def cell_in_span(sheet: str, cell: str, span: str) -> bool:
    target_sheet, _, rest = span.partition("!")
    if sheet != target_sheet:
        return False
    start, _, end = rest.partition(":")
    if not end:
        end = start
    left = _parts(start)
    right = _parts(end)
    here = _parts(cell)
    if left is None or right is None or here is None:
        return False
    cols = sorted((left[0], right[0]))
    rows = sorted((left[1], right[1]))
    return cols[0] <= here[0] <= cols[1] and rows[0] <= here[1] <= rows[1]


def _parts(cell: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"\$?([A-Z]{1,3})\$?(\d+)", cell.upper())
    if not match:
        return None
    return _col_index(match.group(1)), int(match.group(2))


def _ref(token: str) -> Ref:
    match = _CELL.fullmatch(token)
    if not match:
        raise FormulaError("not a cell")
    sheet = match.group(1)[:-1] if match.group(1) else None
    if sheet and sheet.startswith("'") and sheet.endswith("'"):
        sheet = sheet[1:-1].replace("''", "'")
    return Ref(sheet, _col_index(match.group(3)), int(match.group(5)), bool(match.group(2)), bool(match.group(4)))


class _Parser:
    def __init__(self, formula: str) -> None:
        self.tokens = [
            (match.lastgroup, match.group())
            for match in _TOKEN.finditer(formula)
            if match.lastgroup != "ws"
        ]
        self.index = 0
        self.literals: list[str] = []

    def peek(self) -> tuple[str, str] | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def take(self, kind: str | None = None) -> tuple[str, str]:
        token = self.peek()
        if token is None or (kind is not None and token[0] != kind):
            raise FormulaError("unexpected token")
        self.index += 1
        return token

    def parse(self) -> Any:
        if self.peek() is None:
            raise FormulaError("empty")
        tree = self.comparison()
        if self.peek() is not None:
            raise FormulaError("trailing")
        return tree

    def comparison(self) -> Any:
        left = self.expression()
        token = self.peek()
        if token and token[0] == "cmp":
            op = self.take("cmp")[1]
            return Cmp(op, left, self.expression())
        return left

    def expression(self) -> Any:
        left = self.term()
        while self.peek() and self.peek()[0] == "op" and self.peek()[1] in {"+", "-"}:
            op = self.take("op")[1]
            left = Bin(op, left, self.term())
        return left

    def term(self) -> Any:
        left = self.unary()
        while self.peek() and self.peek()[0] == "op" and self.peek()[1] in {"*", "/"}:
            op = self.take("op")[1]
            left = Bin(op, left, self.unary())
        return left

    def unary(self) -> Any:
        if self.peek() and self.peek()[0] == "op" and self.peek()[1] == "-":
            self.take("op")
            return Unary(self.unary())
        return self.primary()

    def primary(self) -> Any:
        token = self.peek()
        if token is None:
            raise FormulaError("missing")
        kind, text = token
        if kind == "number":
            self.take()
            value = Decimal(text)
            self.literals.append(format(value, "f"))
            return Num(value)
        if kind == "string":
            self.take()
            return Text(text[1:-1].replace('""', '"'))
        if kind == "name":
            return self.call()
        if kind == "ref":
            return self.reference()
        if kind == "lparen":
            self.take()
            inner = self.comparison()
            self.take("rparen")
            return inner
        raise FormulaError("unsupported")

    def reference(self) -> Any:
        start = _ref(self.take("ref")[1])
        if self.peek() and self.peek()[0] == "colon":
            self.take("colon")
            end = _ref(self.take("ref")[1])
            return Range(start, end)
        return start

    def call(self) -> Any:
        name = self.take("name")[1].upper()
        if name not in _FUNCTIONS:
            raise FormulaError(f"unsupported function {name}")
        self.take("lparen")
        args: list[Any] = []
        if not (self.peek() and self.peek()[0] == "rparen"):
            args.append(self.comparison())
            while self.peek() and self.peek()[0] == "comma":
                self.take("comma")
                args.append(self.comparison())
        self.take("rparen")
        if name == "IF" and len(args) != 3:
            raise FormulaError("IF needs three arguments")
        if name != "IF" and not args:
            raise FormulaError("empty call")
        return Call(name, tuple(args))


def _r1c1_ref(ref: Ref) -> str:
    row = f"R{ref.row}" if ref.abs_row else f"R[{ref.row}]"
    col = f"C{ref.col}" if ref.abs_col else f"C[{ref.col}]"
    # Relative form is filled in by the caller, which knows the origin.
    return f"{ref.sheet + '!' if ref.sheet else ''}{row}:{col}:{int(ref.abs_row)}:{int(ref.abs_col)}:{ref.row}:{ref.col}"


def _render(tree: Any, origin_sheet: str, origin: tuple[int, int]) -> str:
    if isinstance(tree, Num):
        return format(tree.value, "f")
    if isinstance(tree, Text):
        return '"' + tree.value.replace('"', '""') + '"'
    if isinstance(tree, Ref):
        return _relative(tree, origin_sheet, origin)
    if isinstance(tree, Range):
        return _relative(tree.start, origin_sheet, origin) + ":" + _relative(tree.end, origin_sheet, origin)
    if isinstance(tree, Unary):
        return "-" + _render(tree.expr, origin_sheet, origin)
    if isinstance(tree, Bin):
        return f"({_render(tree.left, origin_sheet, origin)}{tree.op}{_render(tree.right, origin_sheet, origin)})"
    if isinstance(tree, Cmp):
        return f"({_render(tree.left, origin_sheet, origin)}{tree.op}{_render(tree.right, origin_sheet, origin)})"
    if isinstance(tree, Call):
        inner = ",".join(_render(arg, origin_sheet, origin) for arg in tree.args)
        return f"{tree.name}({inner})"
    raise FormulaError("cannot render")


def _relative(ref: Ref, origin_sheet: str, origin: tuple[int, int]) -> str:
    origin_col, origin_row = origin
    if ref.abs_row:
        row = f"R{ref.row}"
    else:
        delta = ref.row - origin_row
        row = "R" if delta == 0 else f"R[{delta}]"
    if ref.abs_col:
        col = f"C{ref.col}"
    else:
        delta = ref.col - origin_col
        col = "C" if delta == 0 else f"C[{delta}]"
    sheet = ""
    if ref.sheet:
        sheet = ref.sheet + "!"
    elif ref.sheet is None:
        sheet = ""
    return sheet + row + col


def parse_formula(formula: str, sheet: str, cell: str) -> Parsed:
    """Parse one formula. Literals are the numbers that are not cell references."""
    body = formula.strip()
    if body.startswith("="):
        body = body[1:]
    if "[" in body or "#REF!" in body.upper():
        raise FormulaError("external or broken marker")
    parser = _Parser(body)
    tree = parser.parse()
    parts = _parts(cell)
    if parts is None:
        raise FormulaError("origin")
    return Parsed(tree, parser.literals, _render(tree, sheet, parts))


@dataclass
class Outcome:
    kind: str
    number: Decimal | None = None
    text: str | None = None
    error: str | None = None


def _blank() -> Outcome:
    return Outcome("blank")


def _num(value: Decimal) -> Outcome:
    return Outcome("number", number=value)


def _err(code: str) -> Outcome:
    return Outcome("error", error=code)


class Evaluator:
    """One pass over a grid. Overrides replace stored numbers and do not write cells."""

    def __init__(self, cells: dict[tuple[str, str], dict], overrides: dict[tuple[str, str], Decimal] | None = None) -> None:
        self.cells = cells
        self.overrides = overrides or {}
        self.sheets = {sheet for sheet, _cell in cells}
        self.memo: dict[tuple[str, str], Outcome] = {}
        self.stack: list[tuple[str, str]] = []
        self.broken: list[dict] = []
        self.cycles: list[list[str]] = []
        self.unsupported: list[dict] = []
        self._seen_cycles: set[tuple[str, ...]] = set()

    def value_of(self, sheet: str, cell: str) -> Outcome:
        key = (sheet, cell)
        if key in self.memo:
            return self.memo[key]
        if key in self.stack:
            start = self.stack.index(key)
            cycle = [f"{item[0]}!{item[1]}" for item in self.stack[start:]]
            signature = tuple(sorted(cycle))
            if signature not in self._seen_cycles:
                self._seen_cycles.add(signature)
                self.cycles.append(sorted(cycle))
            self.memo[key] = _err("circular")
            return self.memo[key]
        row = self.cells.get(key)
        if row is None:
            if sheet not in self.sheets:
                self.broken.append({"cell": None, "target": f"{sheet}!{cell}", "reason": "sheet_not_in_workbook"})
                return _err("broken")
            return _blank()
        formula = row.get("formula")
        if not formula:
            if key in self.overrides:
                return _num(self.overrides[key])
            stored = row.get("value")
            if stored is None or stored == "":
                return _blank()
            try:
                return _num(Decimal(str(stored)))
            except Exception:
                return Outcome("text", text=str(stored))
        self.stack.append(key)
        try:
            parsed = parse_formula(str(formula), sheet, cell)
            outcome = self._eval(parsed.tree, sheet)
        except FormulaError as exc:
            self.unsupported.append({"cell": f"{sheet}!{cell}", "reason": str(exc)})
            outcome = _err("unsupported")
        self.stack.pop()
        if key not in self.memo:
            self.memo[key] = outcome
        return self.memo[key]

    def _eval(self, tree: Any, origin: str) -> Outcome:
        if isinstance(tree, Num):
            return _num(tree.value)
        if isinstance(tree, Text):
            return Outcome("text", text=tree.value)
        if isinstance(tree, Ref):
            sheet = tree.sheet or origin
            if sheet not in self.sheets:
                target = tree.address(origin)
                self.broken.append({"cell": None, "target": target, "reason": "sheet_not_in_workbook"})
                return _err("broken")
            return self.value_of(sheet, f"{_col_name(tree.col)}{tree.row}")
        if isinstance(tree, Range):
            return _err("range")
        if isinstance(tree, Unary):
            inner = self._eval(tree.expr, origin)
            if inner.kind != "number" or inner.number is None:
                return inner if inner.kind == "error" else _err("not_numeric")
            return _num(-inner.number)
        if isinstance(tree, Bin):
            left = self._number(tree.left, origin)
            right = self._number(tree.right, origin)
            if left is None or right is None:
                return _err("not_numeric")
            if tree.op == "+":
                return _num(left + right)
            if tree.op == "-":
                return _num(left - right)
            if tree.op == "*":
                return _num(left * right)
            if tree.op == "/" and right != 0:
                return _num(left / right)
            return _err("divide_by_zero")
        if isinstance(tree, Cmp):
            left = self._eval(tree.left, origin)
            right = self._eval(tree.right, origin)
            if left.kind == "error":
                return left
            if right.kind == "error":
                return right
            return Outcome("number", number=Decimal(1 if _compare(left, right, tree.op) else 0))
        if isinstance(tree, Call):
            return self._call(tree, origin)
        return _err("unsupported")

    def _number(self, tree: Any, origin: str) -> Decimal | None:
        outcome = self._eval(tree, origin)
        if outcome.kind == "blank":
            return Decimal(0)
        if outcome.kind == "number":
            return outcome.number
        return None

    def _call(self, tree: Call, origin: str) -> Outcome:
        if tree.name == "IF":
            condition = self._eval(tree.args[0], origin)
            if condition.kind == "error":
                return condition
            chosen = tree.args[1] if condition.kind == "number" and condition.number else tree.args[2]
            return self._eval(chosen, origin)
        numbers: list[Decimal] = []
        for arg in tree.args:
            if isinstance(arg, Range):
                for sheet, cell in _cells_in_range(arg, origin):
                    if sheet not in self.sheets:
                        self.broken.append(
                            {"cell": None, "target": f"{sheet}!{cell}", "reason": "sheet_not_in_workbook"}
                        )
                        return _err("broken")
                    outcome = self.value_of(sheet, cell)
                    if outcome.kind == "error":
                        return outcome
                    if outcome.kind == "number" and outcome.number is not None:
                        numbers.append(outcome.number)
            else:
                outcome = self._eval(arg, origin)
                if outcome.kind == "error":
                    return outcome
                if outcome.kind == "blank":
                    numbers.append(Decimal(0))
                elif outcome.kind == "number" and outcome.number is not None:
                    numbers.append(outcome.number)
                else:
                    return _err("not_numeric")
        if not numbers:
            return _num(Decimal(0))
        if tree.name == "SUM":
            return _num(sum(numbers, Decimal(0)))
        if tree.name == "AVERAGE":
            return _num(sum(numbers, Decimal(0)) / Decimal(len(numbers)))
        if tree.name == "MIN":
            return _num(min(numbers))
        if tree.name == "MAX":
            return _num(max(numbers))
        return _err("unsupported")


def _cells_in_range(span: Range, origin: str) -> list[tuple[str, str]]:
    sheet = span.start.sheet or span.end.sheet or origin
    other = span.end.sheet or span.start.sheet or origin
    if sheet != other:
        return []
    cols = sorted((span.start.col, span.end.col))
    rows = sorted((span.start.row, span.end.row))
    found = []
    for row in range(rows[0], rows[1] + 1):
        for col in range(cols[0], cols[1] + 1):
            found.append((sheet, f"{_col_name(col)}{row}"))
    return found


def _compare(left: Outcome, right: Outcome, op: str) -> bool:
    if left.kind == "number" and right.kind == "number":
        a, b = left.number, right.number
    elif left.kind == "text" and right.kind == "text":
        a, b = left.text, right.text
    else:
        return False
    if op == "=":
        return a == b
    if op == "<>":
        return a != b
    if op == "<":
        return a < b
    if op == ">":
        return a > b
    if op == "<=":
        return a <= b
    if op == ">=":
        return a >= b
    return False


def walk_refs(tree: Any):
    """Yield cell and range endpoints. The caller decides whether a sheet exists."""
    if isinstance(tree, Ref):
        yield tree
    elif isinstance(tree, Range):
        yield tree.start
        yield tree.end
    elif isinstance(tree, Unary):
        yield from walk_refs(tree.expr)
    elif isinstance(tree, (Bin, Cmp)):
        yield from walk_refs(tree.left)
        yield from walk_refs(tree.right)
    elif isinstance(tree, Call):
        for arg in tree.args:
            yield from walk_refs(arg)


def literal_is_common(literal: str) -> bool:
    """0, 1, and -1 are listed. They are not turned into a question."""
    try:
        return Decimal(literal) in _SKIP_LITERALS
    except Exception:
        return False
