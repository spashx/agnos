"""agnos-trace scorecard: the quality score of a traceability analysis (FTR-TRC-003, ADR-TRC-008).

Each rule of the analysis is a check: its population, its findings (the elements that fail it) and a score from 0 to 10,
ten times the share of the population that is not a finding. The overall score is the average of the checks' scores
weighted by their risk; the grade A to E comes from thresholds. Checks, weights and thresholds are data
(assets/scoring.json, DEC-TRC-032), never code. Python >= 3.9, standard library only.
"""
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# RQ-TRC-067: a literal written more than once is a named constant.
KEY_RISKS = "risks"
KEY_GRADES = "grades"
KEY_VERDICTS = "verdicts"
KEY_ATTENTION = "attention"
KEY_CHECKS = "checks"
KEY_SCORE = "score"
KEY_GRADE = "grade"
KEY_RISK = "risk"
KEY_FINDINGS = "findings"
KEY_POPULATION = "population"
KEY_LABEL = "label"
KEY_TITLE = "title"
KEY_RULE = "rule"
KEY_ITEMS = "items"
KEY_KIND = "kind"
KEY_TYPE = "type"

SCORING_PATH = Path(__file__).resolve().parent.parent / "assets" / "scoring.json"
SCORE_MAX = 10
SCORE_STEP = Decimal("0.1")
TRIGRAM_PART = 1                          # "RQ-ABC-001".split("-")[1]
CONTAINING = "contains"
FUNCTION_FINDINGS = "untraced-functions"


class ScoringError(Exception):
    """The scoring file is unreadable or incomplete."""


# RQ-TRC-059, DEC-TRC-032
def load_scoring(path=SCORING_PATH):
    try:
        scoring = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ScoringError(f"cannot read the scoring file {path}: {error}") from error
    for name in (KEY_RISKS, KEY_GRADES, KEY_VERDICTS, KEY_ATTENTION, KEY_CHECKS):
        if name not in scoring:
            raise ScoringError(f"the scoring file {path} has no '{name}'")
    for check in scoring[KEY_CHECKS]:
        if check[KEY_RISK] not in scoring[KEY_RISKS]:
            raise ScoringError(f"check '{check['key']}' has the unknown risk '{check[KEY_RISK]}'")
    return scoring


def rounded(value):
    """One decimal, halves up, so that the same figures always give the same text."""
    return float(Decimal(value).quantize(SCORE_STEP, rounding=ROUND_HALF_UP))


# RQ-TRC-058
def score_of(population, findings):
    """Ten times the share of the population that is not a finding; None for an empty population."""
    if population <= 0:
        return None
    return rounded(Decimal(SCORE_MAX * (population - findings)) / Decimal(population))


# RQ-TRC-059
def weighted_score(scored, scoring):
    """The average of the (risk, score) pairs weighted by risk; None when no weight is left."""
    pairs = [(scoring[KEY_RISKS][risk], score) for risk, score in scored if score is not None]
    total = sum(weight for weight, _ in pairs)
    if not total:
        return None
    return rounded(sum(Decimal(str(weight)) * Decimal(str(score)) for weight, score in pairs) / Decimal(str(total)))


def grade_of(score, scoring):
    if score is None:
        return None
    for letter, threshold in scoring[KEY_GRADES]:
        if score >= threshold:
            return letter
    return scoring[KEY_GRADES][-1][0]


def trigram_of(element_id):
    return element_id.split("-")[TRIGRAM_PART]


def populations(model, analysis, graph):
    """{population name: the IDs, files or function indexes it holds}, from which the share of findings is read."""
    defined = [e for e in model.elements.values() if e[KEY_KIND] == "element"]
    cited = {dst for (_src, dst, kind) in model.edges if kind != CONTAINING}
    cited |= {e["id"] for e in model.elements.values() if e[KEY_KIND] == "undefined"}
    found = {
        "requirements": [e["id"] for e in defined if e[KEY_TYPE] == "RQ"],
        "tasks": [e["id"] for e in defined if e[KEY_TYPE] == "TASK"],
        "adrs": [e["id"] for e in defined if e[KEY_TYPE] == "ADR"],
        "containers": [e["id"] for e in defined if e[KEY_TYPE] in ("FTR", "ADR", "PLAN")],
        "elements": [e["id"] for e in defined],
        "cited-ids": sorted(cited),
        "files": sorted(model.files),
    }
    if graph is not None:
        found["functions"] = list(range(len(graph.functions)))
    return found


def findings_of(name, analysis, graph):
    if name == FUNCTION_FINDINGS:
        return [n for n, f in enumerate(graph.functions) if not f["ids"]]
    return list(analysis[KEY_FINDINGS][name])


# RQ-TRC-058, RQ-TRC-059, RQ-TRC-064
def build(model, analysis, scoring, graph=None):
    """The `quality` block of the data file: the project's score and grade, its checks, and the same per trigram.

    A check that needs the call graph is left out without it. A trigram's score uses the checks whose findings are
    IDs; files and functions belong to no trigram."""
    pops = populations(model, analysis, graph)
    checks, per_trigram = [], {}
    for spec in scoring[KEY_CHECKS]:
        if spec[KEY_POPULATION] not in pops:
            continue
        found = findings_of(spec[KEY_FINDINGS], analysis, graph)
        population = pops[spec[KEY_POPULATION]]
        score = score_of(len(population), len(found))
        checks.append({"key": spec["key"], KEY_LABEL: spec[KEY_LABEL], KEY_TITLE: spec[KEY_TITLE], KEY_RULE: spec[KEY_RULE],
                       KEY_RISK: spec[KEY_RISK],
                       KEY_ITEMS: spec[KEY_ITEMS], KEY_POPULATION: len(population), KEY_FINDINGS: found, KEY_SCORE: score})
        if spec[KEY_ITEMS] != "id":
            continue
        for tri in sorted({trigram_of(i) for i in population}):
            size = sum(trigram_of(i) == tri for i in population)
            count = sum(trigram_of(i) == tri for i in found)
            per_trigram.setdefault(tri, []).append({"key": spec["key"], KEY_RISK: spec[KEY_RISK], KEY_POPULATION: size,
                                                    KEY_FINDINGS: count, KEY_SCORE: score_of(size, count)})
    score = weighted_score([(c[KEY_RISK], c[KEY_SCORE]) for c in checks], scoring)
    trigrams = {}
    for tri, rows in sorted(per_trigram.items()):
        tri_score = weighted_score([(r[KEY_RISK], r[KEY_SCORE]) for r in rows], scoring)
        trigrams[tri] = {KEY_SCORE: tri_score, KEY_GRADE: grade_of(tri_score, scoring),
                         KEY_CHECKS: [{k: r[k] for k in ("key", KEY_POPULATION, KEY_FINDINGS, KEY_SCORE)} for r in rows]}
    return {KEY_SCORE: score, KEY_GRADE: grade_of(score, scoring), KEY_ATTENTION: scoring[KEY_ATTENTION],
            "scale": scoring[KEY_GRADES], KEY_VERDICTS: scoring[KEY_VERDICTS], KEY_RISKS: scoring[KEY_RISKS],
            KEY_CHECKS: checks, "trigrams": trigrams}


def summary_part(quality):
    """The end of the generator's summary line: grade, score, each check's score, count of findings."""
    scores = ", ".join(f"{c['key']} {'n/a' if c[KEY_SCORE] is None else c[KEY_SCORE]}" for c in quality[KEY_CHECKS])
    shown = "n/a" if quality[KEY_SCORE] is None else f"{quality[KEY_GRADE]} {quality[KEY_SCORE]}/{SCORE_MAX}"
    return f"quality: {shown}; checks: {scores}; findings {sum(len(c[KEY_FINDINGS]) for c in quality[KEY_CHECKS] if c[KEY_RISK] != 'informational')}"
