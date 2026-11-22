#!/usr/bin/env python3
"""The process folder's layout, declared once and copied into each skill (FTR-PLG-006; ADR-PLG-006).

`--write` generates, from agnos-init's `assets/layout.json`, the copies each skill's scripts read: `agnos_layout.py`,
`agnos-layout.ps1` (dot-sourced), `agnos-layout.sh` (sourced), only the languages the skill uses (RQ-PLG-036, DEC-PLG-027).
`--check` compares each copy byte for byte with what it would generate, then reads the Markdown of the delivered skills, the
instructions file and the entry points, and refuses any path of the process folder the layout does not declare, naming the file
and the line (RQ-PLG-037, DEC-PLG-028). A maintainer tool, not delivered. Python >= 3.10, standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILLS = Path(".github") / "skills"
CLAUDE_SKILLS = Path(".claude") / "skills"
SCRIPTS = "scripts"
TESTS = "tests"
SKILL_FILE = "SKILL.md"
MARKDOWN_GLOB = "**/*.md"
LAYOUT_PATH = SKILLS / "agnos-init" / "assets" / "layout.json"
META_PREFIX = "agnos-meta-"
ENTRY_POINTS = (Path(".github") / "instructions" / "agnos-sw-eng.instructions.md", Path("AGENTS.md"), Path("CLAUDE.md"),
                Path("README.md"), Path("CONTRIBUTING.md"))
ENCODING = "utf-8"
EXIT_OK = 0
EXIT_FAILED = 1

PY, PS1, SH = "py", "ps1", "sh"
COPY_NAMES = {PY: "agnos_layout.py", PS1: "agnos-layout.ps1", SH: "agnos-layout.sh"}
COPIES = {                                   # DEC-PLG-027: each skill gets only the languages its scripts are written in
    "agnos-index": (PS1, SH),
    "agnos-init": (PS1, SH),
    "agnos-session": (PS1, SH),              # RQ-INI-018 / DEC-INI-008
    "agnos-perf-center": (PY,),
    "agnos-graph": (PY,),                    # RQ-TRC-133 / DEC-TRC-077
    "agnos-meta-release": (PY,),
    "agnos-meta-plugin-proof": (PY,),
    "agnos-meta-docs-sync": (PY,),
    "agnos-meta-release-prep": (PY,),        # RQ-PLG-027 / DEC-PLG-022
    "agnos-meta-demo": (PS1,),
}
GENERATED_MARK = "GENERATED from agnos-init/assets/layout.json by the layout generator, never edit by hand."
PREFIX = "AGNOS_"
VALUE_RE = re.compile(r"^[\w./-]+$")         # no quote, space or shell character can reach a copy
CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")
LIST_SEPARATOR = " "

FOLDER, SUBFOLDERS, INDEX = "folder", "subfolders", "index"
FILES_IN_FOLDER = ("index", "sessionState", "metricsLog", "projectRules", "perfCenterPage",
                   "graphFile", "guide", "version")   # graphFile: RQ-TRC-129 / DEC-TRC-077        # RQ-PLG-033 / DEC-PLG-026: AGNOS's own files in the folder
LEGACY_FOLDER, LEGACY_INDEX = "legacyFolder", "legacyIndex"
SCRIPT_SUFFIXES = (".py", ".ps1", ".sh")
VENDOR = "vendor"
PATH_CHARS = r"[\w.*<>{}/-]*"
TRAILING = ".-"                               # a sentence's full stop is not part of a path


def constant_name(key):
    """layout.json's camelCase key as an UPPER_SNAKE constant (RQ-PLG-036)."""
    return CAMEL_RE.sub("_", key).upper()


def load(root):
    """The layout of a repository, every value checked safe to copy (RQ-PLG-036)."""
    layout = json.loads((root / LAYOUT_PATH).read_text(encoding=ENCODING))
    for key, value in layout.items():
        for item in value if isinstance(value, list) else [value]:
            if not VALUE_RE.match(item):
                raise ValueError(f"{LAYOUT_PATH.as_posix()}: {key} holds {item!r}, not a plain relative path")
    return layout


def render(layout, language):
    """The bytes of one copy in one language (RQ-PLG-036, DEC-PLG-027)."""
    lines = [f"# {GENERATED_MARK}"]
    for key, value in layout.items():
        name = constant_name(key)
        if language == PY:
            lines.append(f"{name} = {tuple(value)!r}" if isinstance(value, list) else f"{name} = {value!r}")
        elif language == PS1:
            shown = ", ".join(f"'{item}'" for item in value) if isinstance(value, list) else f"'{value}'"
            lines.append(f"${PREFIX}{name} = @({shown})" if isinstance(value, list) else f"${PREFIX}{name} = {shown}")
        else:
            shown = LIST_SEPARATOR.join(value) if isinstance(value, list) else value
            lines.append(f"{PREFIX}{name}='{shown}'")
    return ("\n".join(lines) + "\n").encode(ENCODING)


def copies(root, layout):
    """{path relative to the root: bytes} of every copy (RQ-PLG-036)."""
    return {SKILLS / skill / SCRIPTS / COPY_NAMES[language]: render(layout, language)
            for skill, languages in COPIES.items() for language in languages}


def write(root, layout):
    """Writes every copy; the skill folders must exist (RQ-PLG-036)."""
    for path, data in copies(root, layout).items():
        (root / path).write_bytes(data)
    return []


def declared(layout):
    """(exact paths, prefixes) of the process folder the layout declares, legacy names included (RQ-PLG-037, DEC-PLG-031)."""
    folder = layout[FOLDER]
    exact = {f"{folder}/", *(f"{folder}/{layout[key]}" for key in FILES_IN_FOLDER if key in layout),
             *(f"{folder}/{sub}" for sub in layout[SUBFOLDERS]),
             f"{layout[LEGACY_FOLDER]}/", f"{layout[LEGACY_FOLDER]}/{layout[LEGACY_INDEX]}"}
    prefixes = tuple(f"{folder}/{sub}/" for sub in layout[SUBFOLDERS])
    return exact, prefixes


def markdown_files(root):
    """The Markdown the check reads: delivered skills (tests left out), their Claude pointers, instructions, entry points (RQ-PLG-037)."""
    found = []
    for base, pattern in ((SKILLS, MARKDOWN_GLOB), (CLAUDE_SKILLS, f"*/{SKILL_FILE}")):
        for path in sorted((root / base).glob(pattern)):
            relative = path.relative_to(root / base)
            if not relative.parts[0].startswith(META_PREFIX) and TESTS not in relative.parts[1:]:
                found.append(path)
    return found + [root / entry for entry in ENTRY_POINTS if (root / entry).is_file()]


def cited_paths(layout):
    """The pattern of a path starting with the folder's name or the legacy one (RQ-PLG-037)."""
    names = "|".join(re.escape(name) for name in sorted({layout[FOLDER], layout[LEGACY_FOLDER]}))
    return re.compile(rf"(?<![\w./-])(?:{names})/{PATH_CHARS}")


def delivered_scripts(root):
    """The scripts of the delivered skills, their generated copies, tests and vendored code left out (RQ-PLG-036)."""
    copy_names = set(COPY_NAMES.values())
    found = []
    for path in sorted((root / SKILLS).glob(f"*/{SCRIPTS}/**/*")):
        relative = path.relative_to(root / SKILLS)
        if (path.suffix in SCRIPT_SUFFIXES and not relative.parts[0].startswith(META_PREFIX)
                and path.name not in copy_names and VENDOR not in relative.parts):
            found.append(path)
    return found


def script_literals(layout):
    """The names a delivered script may hold only through its copy: the files, their base names and the subfolders (RQ-PLG-036)."""
    names = {layout[key] for key in (*FILES_IN_FOLDER, LEGACY_INDEX) if key in layout}   # an older commit may lack a newer key | set(layout[SUBFOLDERS])
    return sorted(names | {name.rsplit("/", 1)[-1] for name in names}, key=len, reverse=True)


def check_scripts(root, layout):
    """Findings for each line of a delivered script naming the folder or a name of the layout (RQ-PLG-036)."""
    findings = []
    # a name standing alone: inside a word, such as the copy's own constant AGNOS_VERSION, or after a dot, such as
    # agnos_layout.VERSION, it is the copy's constant, not the layout's value (TASK-PLG-050)
    literals = [(name, re.compile(rf"(?<![\w.-]){re.escape(name)}(?![\w-])")) for name in script_literals(layout)]
    pattern = cited_paths(layout)
    for path in delivered_scripts(root):
        for number, line in enumerate(path.read_text(encoding=ENCODING).splitlines(), start=1):
            held = next((name for name, alone in literals if alone.search(line)), None) or next(
                (match.group() for match in pattern.finditer(line)), None)
            if held:
                findings.append(f"{path.relative_to(root).as_posix()}:{number}: {held} is the layout's, read it from the copy")
    return findings


def check(root, layout):
    """Findings 'file:line: what' for each copy that differs, each layout name in a delivered script and each undeclared
    path cited in the Markdown (RQ-PLG-036, RQ-PLG-037)."""
    findings = check_scripts(root, layout)
    for path, data in copies(root, layout).items():
        target = root / path
        if not target.is_file():
            findings.append(f"{path.as_posix()}: missing, run layout.py --write")
        elif target.read_bytes() != data:
            findings.append(f"{path.as_posix()}: differs from layout.json, run layout.py --write")
    exact, prefixes = declared(layout)
    pattern = cited_paths(layout)
    for path in markdown_files(root):
        for number, line in enumerate(path.read_text(encoding=ENCODING).splitlines(), start=1):
            for match in pattern.finditer(line):
                cited = match.group().rstrip(TRAILING)
                if cited not in exact and not cited.startswith(prefixes):
                    findings.append(f"{path.relative_to(root).as_posix()}:{number}: {cited} is not declared by the layout")
    return findings


def main(argv=None):
    """Writes or checks the copies; prints the findings, exit 1 on any (RQ-PLG-036, RQ-PLG-037)."""
    parser = argparse.ArgumentParser(description="The process folder's layout: generate its copies or check them.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="generate every copy from layout.json")
    action.add_argument("--check", action="store_true", help="compare the copies and the Markdown with layout.json")
    parser.add_argument("--root", default=str(ROOT), help="the repository (default: this one)")
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        layout = load(root)
        findings = write(root, layout) if args.write else check(root, layout)
    except (OSError, ValueError) as error:
        print(f"layout: {error}", file=sys.stderr)
        return EXIT_FAILED
    for finding in findings:
        print(finding)
    print(f"layout: {'written' if args.write else 'checked'}, {len(findings)} findings")
    return EXIT_FAILED if findings else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
