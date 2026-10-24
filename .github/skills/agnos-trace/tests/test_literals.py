"""Test of the skill's code against duplicated literals (RQ-TRC-067, TASK-TRC-052): a string of four characters or more,
or a number other than 0, 1 and 2, that a script writes more than once is a named constant.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import ast
import re
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
ASSETS = SKILL / "assets"
PYTHON_SCRIPTS = ("trace_matrix.py", "callgraph.py", "scorecard.py")
PAGE_SCRIPT = ASSETS / "matrix.js"
STRING_MIN = 4
FREE_NUMBERS = frozenset({0, 1, 2})
SHOWN = 12

JS_TOKEN_RE = re.compile(r"""
    (?P<comment>//[^\n]*|/\*.*?\*/)
  | (?P<template>`(?:\\.|[^`\\])*`)
  | (?P<string>"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')
  | (?P<number>(?<![\w.$])\d+(?:\.\d+)?(?![\w.]))
""", re.S | re.X)


def is_constant_name(name):
    return name.isupper() or (name.replace("_", "").isalnum() and name == name.upper() and any(c.isalpha() for c in name))


def python_literals(path):
    """Every string of STRING_MIN characters or more and every number outside FREE_NUMBERS in a Python file, apart from
    docstrings, the text parts of f-strings and the definitions of the named constants themselves."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skipped = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and is_constant_name(t.id) for t in node.targets):
            skipped.update(id(part) for part in ast.walk(node.value))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                skipped.add(id(first.value))
        if isinstance(node, ast.JoinedStr):
            skipped.update(id(part) for part in node.values)
    found = Counter()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or id(node) in skipped or isinstance(node.value, bool):
            continue
        value = node.value
        if isinstance(value, str) and len(value) >= STRING_MIN or isinstance(value, (int, float)) and value not in FREE_NUMBERS:
            found[repr(value)] += 1
    return found


JS_CONSTANT_RE = re.compile(r"^[ ]{0,4}const[ ]+[A-Z][A-Z0-9_]*[ ]*=", re.M)
JS_OPEN = "([{"
JS_CLOSE = ")]}"


def js_constant_spans(text):
    """The (start, end) of each statement that defines a named constant: from `const NAME =` to its `;`."""
    spans = []
    for start in (m.start() for m in JS_CONSTANT_RE.finditer(text)):
        depth, i = 0, start
        while i < len(text):
            token = JS_TOKEN_RE.match(text, i)
            if token and token.lastgroup != "number" and token.start() == i:
                i = token.end()
                continue
            char = text[i]
            depth += char in JS_OPEN
            depth -= char in JS_CLOSE
            if char == ";" and depth <= 0:
                break
            i += 1
        spans.append((start, i))
    return spans


def js_literals(path):
    """The same for the page script, read by a tokenizer that leaves comments, template literals and the definitions of
    named constants aside."""
    text = path.read_text(encoding="utf-8")
    spans = js_constant_spans(text)
    found = Counter()
    for match in JS_TOKEN_RE.finditer(text):
        if any(a <= match.start() < b for a, b in spans):
            continue
        kind, literal = match.lastgroup, match.group()
        if kind == "string" and len(literal) - 2 >= STRING_MIN:
            found[literal[1:-1]] += 1
        elif kind == "number" and float(literal) not in FREE_NUMBERS:
            found[literal] += 1
    return found


class RepeatedLiteralTest(unittest.TestCase):
    """TASK-TRC-052: RQ-TRC-067 (maintainability: AGNOS section 4, no duplicated literal)."""

    def repeated(self, counter):
        return sorted(((n, lit) for lit, n in counter.items() if n > 1), reverse=True)

    def test_RQ_TRC_067_given_each_script_when_its_literals_are_listed_then_none_is_written_more_than_once(self):
        report = {}
        for name in PYTHON_SCRIPTS:
            repeated = self.repeated(python_literals(SCRIPTS / name))
            if repeated:
                report[name] = repeated[:SHOWN] + [(len(repeated), "repeated in all")]
        self.assertEqual({}, report)

    def test_RQ_TRC_067_given_the_page_script_when_its_literals_are_listed_then_none_is_written_more_than_once(self):
        repeated = self.repeated(js_literals(PAGE_SCRIPT))
        self.assertEqual([], repeated[:SHOWN] + [(len(repeated), "repeated in all")] if repeated else [])


if __name__ == "__main__":
    unittest.main()
