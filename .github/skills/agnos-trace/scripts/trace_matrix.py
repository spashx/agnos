#!/usr/bin/env python3
"""agnos-trace: the traceability matrix of an AGNOS process and its sources, as one self-contained HTML page.

Implements FTR-TRC-001 after ADR-TRC-001, ADR-TRC-002 and ADR-TRC-003. Procedure and options: ../SKILL.md.
Python >= 3.9, standard library only (DEC-TRC-001, RQ-TRC-021). Knows the AGNOS ID grammar and the INDEX.idx.md format,
nothing of the product being developed (RQ-TRC-019).
"""
import argparse
import re
import sys
from pathlib import Path

INDEX_NAME = "INDEX.idx.md"
DEFAULT_OUT_NAME = "TRACEABILITY.html"
TYPES = ("FTR", "RQ", "ADR", "DEC", "PLAN", "TASK")
ID_PATTERN = r"(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-[0-9]{3}"
NUMBER_LENGTH = 3
PREFIX_CUT = -(NUMBER_LENGTH + 1)              # "RQ-ABC-001"[:PREFIX_CUT] == "RQ-ABC"
LINE_TEXT_MAX = 200                            # characters of a line kept as evidence (DEC-TRC-003)

# DEC-TRC-003: an ID is not part of a longer word or number; a range is "<A> to <B>", "<A>–<B>", "<A>—<B>", "<A>..<B>"
# or "<A>-<B>".
ID_RE = re.compile(rf"(?<![A-Za-z0-9]){ID_PATTERN}(?![0-9])")
FULL_ID_RE = re.compile(rf"^{ID_PATTERN}$")
RANGE_RE = re.compile(rf"(?<![A-Za-z0-9])({ID_PATTERN})(?:\s+to\s+|\s*(?:–|—|\.\.|-)\s*)({ID_PATTERN})(?![0-9])")


class InputError(Exception):
    """An input the generator cannot work from (RQ-TRC-002)."""


# ---- IDs ---------------------------------------------------------------------------------------------------------
# RQ-TRC-005, DEC-TRC-003
def extract_ids(text, defined):
    """Every AGNOS ID of the text, a range of one type and trigram counting as the defined IDs between its two ends."""
    found = {m.group(0) for m in ID_RE.finditer(text)}
    for m in RANGE_RE.finditer(text):
        low, high = m.group(1), m.group(2)
        prefix = low[:PREFIX_CUT]
        if prefix != high[:PREFIX_CUT] or low >= high:
            continue
        lo, hi = int(low[PREFIX_CUT + 1:]), int(high[PREFIX_CUT + 1:])
        found.update(i for i in defined if i[:PREFIX_CUT] == prefix and lo < int(i[PREFIX_CUT + 1:]) < hi)
    return found


def id_type(element_id):
    return element_id.split("-", 1)[0]


def evidence(line_number, text):
    """A line kept as the proof of a link: its number and its text, trimmed (DEC-TRC-003)."""
    return [line_number, text.strip()[:LINE_TEXT_MAX]]


# ---- model -------------------------------------------------------------------------------------------------------
# DEC-TRC-002
class Model:
    """The traceability graph: elements (process elements, undefined IDs), source files, and the links between them."""

    def __init__(self):
        self.elements = {}   # id -> element dict, in index order
        self.edges = {}      # (source, target, kind) -> list of [line, text]; kind: contains | refs | code
        self.files = {}      # source path -> {"path", "ids"}

    def add_element(self, element):
        self.elements[element["id"]] = element

    def ensure(self, element_id):
        """The element of an ID, made an undefined element when the index does not define it (RQ-TRC-007)."""
        if element_id not in self.elements:
            self.add_element({"id": element_id, "kind": "undefined", "type": id_type(element_id),
                              "tri": element_id.split("-")[1], "doc": "", "first": 0, "last": 0, "status": "",
                              "title": "Not defined in the index"})
        return self.elements[element_id]

    def add_edge(self, source, target, kind, proof=None):
        lines = self.edges.setdefault((source, target, kind), [])
        if proof is not None:
            lines.append(proof)


# ---- process -----------------------------------------------------------------------------------------------------
# RQ-TRC-003
def parse_index(index_path):
    """The rows of INDEX.idx.md: one element per 'ID|first-last|status|title' row, under its '@document' line."""
    rows, doc = [], ""
    for raw in index_path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("@"):
            doc = raw[1:].strip()
            continue
        parts = raw.split("|", 3)
        if len(parts) != 4 or not FULL_ID_RE.match(parts[0]):
            continue
        first, _, last = parts[1].partition("-")
        rows.append({"id": parts[0], "kind": "element", "type": id_type(parts[0]), "tri": parts[0].split("-")[1],
                     "doc": doc, "first": int(first), "last": int(last or first), "status": parts[2].strip(),
                     "title": parts[3].strip()})
    return rows


def resolve_document(process_dir, doc):
    """A document path of the index: relative to the process folder's parent, else to the process folder itself."""
    candidates = [process_dir.parent / doc, process_dir / Path(*Path(doc).parts[1:]) if len(Path(doc).parts) > 1
                  else process_dir / doc, process_dir / doc]
    return next((c for c in candidates if c.is_file()), None)


# RQ-TRC-004, DEC-TRC-003
def add_containment(model, members):
    """Links each element of one document to the element whose range most closely encloses its own."""
    for child in members:
        parents = [p for p in members if p is not child and p["first"] <= child["first"] and child["last"] <= p["last"]
                   and (p["first"], p["last"]) != (child["first"], child["last"])]
        if parents:
            parent = min(parents, key=lambda p: p["last"] - p["first"])
            model.add_edge(parent["id"], child["id"], "contains")


# RQ-TRC-005, RQ-TRC-007, DEC-TRC-003
def add_document_references(model, members, lines, defined):
    """Links each element to the IDs of its own lines: those of its range that no element it contains holds."""
    owner = [None] * (len(lines) + 1)
    for element in sorted(members, key=lambda e: e["last"] - e["first"], reverse=True):
        for ln in range(element["first"], min(element["last"], len(lines)) + 1):
            owner[ln] = element["id"]
    for ln, text in enumerate(lines, 1):
        if owner[ln] is None:
            continue
        for target in sorted(extract_ids(text, defined) - {owner[ln]}):
            model.ensure(target)
            model.add_edge(owner[ln], target, "refs", evidence(ln, text))


def build_process_model(process_dir):
    """The elements of the process folder's index, their containment and their references (TASK-TRC-001)."""
    process_dir = Path(process_dir)
    index_path = process_dir / INDEX_NAME
    if not index_path.is_file():
        raise InputError(f"{index_path} not found: run the agnos-index skill first, or give the folder holding it")
    model = Model()
    rows = parse_index(index_path)
    for row in rows:
        model.add_element(row)
    defined = set(model.elements)
    by_doc = {}
    for row in rows:
        by_doc.setdefault(row["doc"], []).append(row)
    for doc, members in by_doc.items():
        add_containment(model, members)
        path = resolve_document(process_dir, doc)
        if path is None:
            print(f"agnos-trace: warning: {doc} not found, its references are not read", file=sys.stderr)
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        add_document_references(model, members, lines, defined)
    return model


# ---- command line ------------------------------------------------------------------------------------------------
# RQ-TRC-001
def parse_args(argv):
    parser = argparse.ArgumentParser(prog="trace_matrix.py", description="AGNOS traceability matrix (FTR-TRC-001)")
    parser.add_argument("--process", required=True, help=f"AGNOS process folder holding {INDEX_NAME}")
    parser.add_argument("--sources", required=True, action="append", help="source folder to scan (repeatable)")
    parser.add_argument("--out", help=f"output page (default: <process>/{DEFAULT_OUT_NAME})")
    return parser.parse_args(argv)


# RQ-TRC-002
def check_sources(sources):
    missing = [s for s in sources if not Path(s).is_dir()]
    if missing:
        raise InputError("source folder not found: " + ", ".join(missing))


def main(argv=None):
    args = parse_args(argv)
    try:
        check_sources(args.sources)
        build_process_model(args.process)
    except InputError as error:
        print(f"agnos-trace: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
