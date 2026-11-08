"""agnos-meta-website: builds the AGNOS presentation website from the Markdown and the images of the skill's assets
(FTR-WEB-001; ADR-WEB-001). <!-- RQ-WEB-001, RQ-WEB-003, RQ-WEB-016 / DEC-WEB-001 -->

Usage (standard library only):
  python -I build_site.py build --demo <demo repository> --out <folder>

The build reads assets/content/en.md and fr.md, checks that both hold the same fields and that the template
assets/template.html uses exactly them, measures the demo's index, and writes one page: English in the markup, French in
a dictionary that the page's language switch applies. Exit 0: the site is written and one summary line is printed.
Exit 1: one error per line on the error stream, and nothing is written.
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

# RQ-WEB-003, DEC-WEB-003: the assets
SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"
TEMPLATE = "template.html"
CONTENT = "content"
MARKDOWN = ".md"
LANGUAGES = ("en", "fr")
SOURCE_LANGUAGE = "en"
FRENCH = "fr"
ENCODING = "utf-8"
PAGE = "index.html"

# RQ-WEB-005: the demo's process documents and index
PROCESS = "agnos-process"
PROCESS_FOLDERS = ("1.requirements", "2.architecture", "3.plan")
INDEX = "process.idx.md"
KILO = 1000
DECIMALS = {"en": ".", "fr": ","}
NBSP = " "
NARROW_NBSP = " "
UNITS = {"en": " KB", "fr": NBSP + "Ko"}
SIZE_FORMAT = "{:.1f}"
RATIO_FORMAT = "1/{}"
SHARE_DIGITS = 1
PERCENT = 100
DEMO_LINK = "demo/PERF-CENTER.html"

# RQ-WEB-006: French typography
APOSTROPHE = "'"
TYPOGRAPHIC_APOSTROPHE = "’"
FRENCH_COLON = re.compile(r" :")
FRENCH_MARKS = re.compile(r" ([;?!])")

# RQ-WEB-003: the content's format
COMMENT = re.compile(r"<!--.*?-->", re.S)
SECTION = re.compile(r"^##\s+([a-z0-9-]+)\s*$")
FIELD = re.compile(r"^###\s+([a-z0-9-]+)\s*$")
FENCE = "```"
LIST_ITEM = re.compile(r"^-\s+(.+)$")
SHOT = re.compile(r"^\[!\[([^\]]+)\]\(([^)\s]+)\)\]\(([^)\s]+)\)$")
INLINE = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*|\[([^\]]+)\]\(([^)\s]+)\)")
VARIABLE = re.compile(r"\{\{([a-z0-9.-]+)\}\}")
HARD_BREAK = "\\"
LINE_BREAK = "<br>"
PATH_LINE = "@"            # an index excerpt's document line, dimmed
OPEN_ARROW = "↗"
LABELS_SECTION = "labels."
OPEN_LABEL = "labels.open"

# DEC-WEB-003: the template's slots
SLOT = re.compile(r'(<(?P<tag>[a-z0-9]+)\b[^>]*?\sdata-i18n="(?P<key>[^"]+)"[^>]*>)(</(?P=tag)>)')
ANY_SLOT = re.compile(r'\sdata-i18n="([^"]+)"')
ATTRIBUTE_SLOT = re.compile(r'\sdata-i18n-attr="(?P<name>[a-z-]+)=(?P<key>[a-z0-9.-]+)"')
TEMPLATE_VALUE = re.compile(r"\{\{v:([a-z0-9.-]+)\}\}")
TAG = re.compile(r"<[^>]+>")
FR_MARKER = "/*@FR@*/{}"
LESS_THAN = "<"
LESS_THAN_ESCAPE = "\\u003c"

KIND_TEXT, KIND_LIST, KIND_SHOT, KIND_CODE = "text", "list", "shot", "code"
REPORT = "agnos-meta-website: "


def read(path):
    """The text of a UTF-8 file. RQ-WEB-003"""
    return Path(path).read_text(encoding=ENCODING)


def escape(text):
    """Text made safe for HTML content and attributes. RQ-WEB-003"""
    return html.escape(text, quote=True)


def strip_blank(lines):
    """Lines without their leading and trailing blank lines. RQ-WEB-003"""
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


class ContentReader:
    """Reads one content file line by line into {section.field: lines}. RQ-WEB-003, RQ-WEB-004"""

    def __init__(self, name, errors):
        self.name, self.errors = name, errors
        self.fields, self.section, self.key, self.fenced = {}, None, None, False

    def report(self, number, message):
        """One misplaced line, with its file and line number. RQ-WEB-004"""
        self.errors.append(f"{self.name}:{number}: {message}")

    def add(self, line):
        """A line of the current field, if any. RQ-WEB-003"""
        if self.key is not None:
            self.fields[self.key].append(line)

    def open_field(self, number, field):
        """A new field of the current section. RQ-WEB-003, RQ-WEB-004"""
        if self.section is None:
            self.report(number, "a field before any section")
            return
        self.key = f"{self.section}.{field}"
        if self.key in self.fields:
            self.report(number, f"{self.key} is defined twice")
        self.fields[self.key] = []

    def line(self, number, line):
        """Places one line: inside a fenced block, a heading, text or a blank line. RQ-WEB-003, RQ-WEB-004"""
        fence = line.strip() == FENCE
        if self.fenced or fence:
            self.fenced = self.fenced != fence
            self.add(line)
            return
        section_match, field_match = SECTION.match(line), FIELD.match(line)
        if section_match:
            self.section, self.key = section_match.group(1), None
        elif field_match:
            self.open_field(number, field_match.group(1))
        elif line.strip() and self.key is None:
            self.report(number, "text outside a field")
        else:
            self.add(line if line.strip() else "")


def parse(path, name, errors):
    """{section.field: lines} of one content file; misplaced text is reported with its line number. RQ-WEB-003,
    RQ-WEB-004"""
    text = COMMENT.sub(lambda match: "\n" * match.group(0).count("\n"), read(path))
    reader = ContentReader(name, errors)
    for number, line in enumerate(text.splitlines(), 1):
        reader.line(number, line)
    return {key: strip_blank(lines) for key, lines in reader.fields.items()}


def typography(text, language):
    """French spacing and apostrophes; other languages unchanged. RQ-WEB-006"""
    if language != FRENCH:
        return text
    text = text.replace(APOSTROPHE, TYPOGRAPHIC_APOSTROPHE)
    text = FRENCH_COLON.sub(NBSP + ":", text)
    return FRENCH_MARKS.sub(NARROW_NBSP + r"\1", text)


def inline(text, language):
    """HTML of one line: `code`, **strong**, *emphasis* and [links](address); everything else escaped. RQ-WEB-003"""
    out, position = [], 0
    for match in INLINE.finditer(text):
        out.append(escape(typography(text[position:match.start()], language)))
        code, strong, emphasis, label, address = match.groups()
        if code is not None:
            out.append("<code>" + escape(code) + "</code>")
        elif strong is not None:
            out.append("<strong>" + escape(typography(strong, language)) + "</strong>")
        elif emphasis is not None:
            out.append("<em>" + escape(typography(emphasis, language)) + "</em>")
        else:
            out.append(f'<a href="{escape(address)}">{escape(typography(label, language))}</a>')
        position = match.end()
    out.append(escape(typography(text[position:], language)))
    return "".join(out)


def substitute(line, values, where, errors):
    """A line with its {{variables}} replaced by the measured values. RQ-WEB-005"""
    def value(match):
        if match.group(1) not in values:
            errors.append(f"{where}: unknown variable {match.group(0)}")
            return match.group(0)
        return values[match.group(1)]
    return VARIABLE.sub(value, line)


def code_block(lines):
    """An index excerpt: its lines kept, its document lines dimmed. RQ-WEB-003"""
    return "\n".join(f"<span>{escape(line)}</span>" if line.startswith(PATH_LINE) else escape(line)
                     for line in lines[1:-1])


def paragraph(lines, language):
    """One paragraph's HTML; a line ending in a backslash forces a line break. RQ-WEB-003"""
    parts = []
    for number, line in enumerate(lines):
        broken = line.endswith(HARD_BREAK)
        parts.append(inline(line[:-len(HARD_BREAK)].rstrip() if broken else line, language))
        if number < len(lines) - 1:
            parts.append(LINE_BREAK if broken else " ")
    return "".join(parts)


def render(key, lines, language, values, errors):
    """(kind, payload) of a field: text, list, shot (alt, src, href) or code; None on error. RQ-WEB-003, RQ-WEB-004"""
    where = f"{language}{MARKDOWN}: {key}"
    if not lines:
        errors.append(where + " is empty")
        return None
    if lines[0].strip() == FENCE:
        return KIND_CODE, code_block(lines)
    if any(not line.strip() for line in lines):
        errors.append(where + " holds more than one paragraph")
        return None
    lines = [substitute(line.strip(), values, where, errors) for line in lines]
    items = [LIST_ITEM.match(line) for line in lines]
    if all(items):
        return KIND_LIST, [inline(item.group(1).strip(), language) for item in items]
    if any(items):
        errors.append(where + " mixes a list and a paragraph")
        return None
    shot = SHOT.match(lines[0])
    if shot:
        if len(lines) > 1:
            errors.append(where + " holds more than its image")
            return None
        alt, src, href = shot.groups()
        return KIND_SHOT, (typography(alt, language), src, href)
    return KIND_TEXT, paragraph(lines, language)


def shot_html(alt, src, href, open_label):
    """A screenshot that opens the demo, with its "open in the demo" label. RQ-WEB-011"""
    label = f'<span class="shot-open">{open_label} {OPEN_ARROW}</span>' if open_label else ""
    image = f'<img src="{escape(src)}" alt="{escape(alt)}" loading="lazy">'
    return f'<a class="shot-link" href="{escape(href)}" target="_blank" rel="noopener">{image}{label}</a>'


def measure(demo):
    """Bytes of the demo's process documents and of its index. RQ-WEB-005"""
    root = Path(demo) / PROCESS
    documents = sum(path.stat().st_size for folder in PROCESS_FOLDERS for path in (root / folder).glob("*" + MARKDOWN))
    return documents, (root / INDEX).stat().st_size


def size_text(size, language):
    """A size in kilobytes, written for the language. RQ-WEB-005"""
    return SIZE_FORMAT.format(size / KILO).replace(".", DECIMALS[language]) + UNITS[language]


def render_language(language, fields, values, assets, errors, images):
    """{key: html} of one language; a missing image is reported. RQ-WEB-003, RQ-WEB-004"""
    parsed = {key: render(key, lines, language, values, errors) for key, lines in fields.items()}
    open_result = parsed.get(OPEN_LABEL)
    open_label = open_result[1] if open_result and open_result[0] == KIND_TEXT else ""
    rendered = {}
    for key, result in parsed.items():
        if result is not None:
            rendered[key] = field_html(language, key, result, open_label, assets, errors, images)
    return rendered


def field_html(language, key, result, open_label, assets, errors, images):
    """The HTML of one rendered field; a missing image is reported. RQ-WEB-003, RQ-WEB-004"""
    kind, payload = result
    if kind == KIND_SHOT:
        alt, src, href = payload
        images.add(src)
        if not (Path(assets) / src).is_file():
            errors.append(f"{language}{MARKDOWN}: {key}: {src} does not exist")
        return shot_html(alt, src, href, open_label)
    if kind == KIND_LIST:
        return "".join(f"<li>{item}</li>" for item in payload)
    return payload


def read_content(assets, errors):
    """{language: {key: lines}}; a field missing from one language is reported. RQ-WEB-003, RQ-WEB-004"""
    fields = {lang: parse(Path(assets) / CONTENT / (lang + MARKDOWN), lang + MARKDOWN, errors) for lang in LANGUAGES}
    for lang in LANGUAGES:
        for other in LANGUAGES:
            for key in sorted(set(fields[other]) - set(fields[lang])):
                errors.append(f"{lang}{MARKDOWN}: {key} is missing (it is in {other}{MARKDOWN})")
    return fields


def fill_template(template, source, template_values, errors):
    """(page, keys used): the English text in the slots, attributes and values of the template. RQ-WEB-003,
    RQ-WEB-004, RQ-WEB-007"""
    used = set()

    def value(match):
        if match.group(1) not in template_values:
            errors.append(f"template: unknown value {match.group(0)}")
            return match.group(0)
        return escape(template_values[match.group(1)])

    def attribute(match):
        key = match.group("key")
        used.add(key)
        if key not in source:
            errors.append(f"template: {key} has no text in the content")
            return match.group(0)
        return f'{match.group(0)} {match.group("name")}="{escape(TAG.sub("", source[key]))}"'

    def element(match):
        key = match.group("key")
        used.add(key)
        if key not in source:
            errors.append(f"template: {key} has no text in the content")
            return match.group(0)
        return match.group(1) + source[key] + match.group(4)

    page = SLOT.sub(element, ATTRIBUTE_SLOT.sub(attribute, TEMPLATE_VALUE.sub(value, template)))
    for key in sorted(set(ANY_SLOT.findall(template)) - used):
        errors.append(f"template: the element of {key} must be empty")
    return page, used


def french_dictionary(template, french):
    """The French texts of the page: element HTML and plain attribute text. RQ-WEB-007"""
    elements = set(ANY_SLOT.findall(template))
    attributes = {match.group("key") for match in ATTRIBUTE_SLOT.finditer(template)}
    data = {"html": {key: french[key] for key in sorted(elements) if key in french},
            "attr": {key: TAG.sub("", french[key]) for key in sorted(attributes) if key in french}}
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(LESS_THAN, LESS_THAN_ESCAPE)


def build_page(assets, demo, errors, tokens_css=""):
    """(page, summary) built from the assets and the demo, or None when an error was found. RQ-WEB-003 to
    RQ-WEB-007"""
    template = read(Path(assets) / TEMPLATE)
    fields = read_content(assets, errors)
    documents, index = measure(demo)
    images, rendered = set(), {}
    for lang in LANGUAGES:
        values = {"index.documents": size_text(documents, lang), "index.size": size_text(index, lang),
                  "index.ratio": RATIO_FORMAT.format(round(documents / index))}
        rendered[lang] = render_language(lang, fields[lang], values, assets, errors, images)
    template_values = {"index.share": str(round(PERCENT * index / documents, SHARE_DIGITS)), "link.demo": DEMO_LINK}
    source = rendered[SOURCE_LANGUAGE]
    page, used = fill_template(template, source, template_values, errors)
    used.add(OPEN_LABEL)
    for key in sorted(set(source) - used):
        errors.append(f"content: {key} is used by no element of the template")
    if template.count(FR_MARKER) != 1:
        errors.append("template: the French marker must appear exactly once")
    page = page.replace(FR_MARKER, french_dictionary(template, rendered[FRENCH]))
    summary = f"{len(source)} fields in each language, {len(images)} images, index {values['index.ratio']}"
    return None if errors else (page, summary)


def main(argv=None):
    """Parse the arguments, build, write the site or report the errors. RQ-WEB-001"""
    parser = argparse.ArgumentParser(prog="agnos-meta-website", description="Build the AGNOS presentation website.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="build the site into a folder")
    build.add_argument("--demo", required=True, help="the demo repository, whose index is measured")
    build.add_argument("--out", required=True, help="the folder to write the site into")
    args = parser.parse_args(argv)
    errors = []
    result = build_page(ASSETS_DIR, args.demo, errors)
    if result is None:
        for error in errors:
            print(REPORT + error, file=sys.stderr)
        return 1
    page, summary = result
    os.makedirs(args.out, exist_ok=True)
    (Path(args.out) / PAGE).write_text(page, encoding=ENCODING)
    print(f"{REPORT}{summary}; {args.out} written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
