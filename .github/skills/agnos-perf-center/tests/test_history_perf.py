"""Measure of the contribution history's speed and size (RQ-HST-013, TASK-HST-007), on a generated repository of 2,000
commits by 12 identities, 300 process elements and 500 source files.

Run from the repository root with AGNOS_PERF_CENTER_PERF=1: python -m unittest discover -s .github/skills/agnos-perf-center/tests -p test_history_perf.py -v
The repository is written in one `git fast-import`, with an empty global git configuration.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import agnos_layout  # noqa: E402  RQ-PLG-036: the index and log names, as the scripts read them
sys.path.insert(0, str(HERE))

from test_perf_center import BROWSER, rendered_dom_after, run_main  # noqa: E402

PERF = os.environ.get("AGNOS_PERF_CENTER_PERF") == "1"
COMMITS = 2000
HUMANS = 10
AGENTS = ("Claude Opus 5.5 <noreply@anthropic.com>", "Claude Sonnet 5.5 <noreply@anthropic.com>")
FEATURES = 10
REQUIREMENTS_PER_FEATURE = 29                       # 10 features and 290 requirements: 300 elements
LINES_PER_REQUIREMENT = 5
FOLDERS = 25
FILES_PER_FOLDER = 20                              # 500 source files
START = 1767225600                                  # 2026-01-01, UTC
STEP = 3 * 3600                                     # a commit every three hours
MAX_SECONDS = 20                                    # RQ-HST-013's metrics
MAX_BYTES = 3 * 1024 * 1024
MAX_DRAW_MS = 300
MAX_STEP_MS = 50
P95 = 0.95
STEPS = 50


def requirement_id(feature, n):
    return f"RQ-PRF-{feature * REQUIREMENTS_PER_FEATURE + n + 1:03d}"


def feature_lines(feature):
    lines = [f"# FTR-PRF-{feature + 1:03d}: Feature {feature + 1}", ""]
    for n in range(REQUIREMENTS_PER_FEATURE):
        lines += [f"### {requirement_id(feature, n)}: Requirement {n}", "- **Statement**: the system SHALL work.",
                  "- **Priority**: Must", "- **Acceptance Criteria**: Given, When, Then.", ""]
    return lines


def write_repository(top):
    """The repository and its process index; returns the process and source folders."""
    people = [f"Dev {n} <dev{n}@example.com>" for n in range(HUMANS)]
    docs = {f"process/1.requirements/FTR-PRF-{f + 1:03d}.md": feature_lines(f) for f in range(FEATURES)}
    sources = {f"src/m{d:02d}/f{n:03d}.py": [f"# {requirement_id((d * FILES_PER_FOLDER + n) % FEATURES, n % REQUIREMENTS_PER_FEATURE)}",
                                             "def run():", "    return 0"]
               for d in range(FOLDERS) for n in range(FILES_PER_FOLDER)}
    stream = []

    def data(text):
        raw = text.encode("utf-8")
        stream.append(f"data {len(raw)}\n".encode("utf-8") + raw + b"\n")

    doc_paths, source_paths = sorted(docs), sorted(sources)
    for c in range(COMMITS):
        author = people[c % HUMANS] if c % 20 else AGENTS[c % 2]
        message = f"change {c}" + (f"\n\nCo-Authored-By: {AGENTS[c % 2]}" if c % 2 and c % 20 else "")
        stream.append(f"commit refs/heads/main\nmark :{c + 1}\nauthor {author} {START + c * STEP} +0000\n"
                      f"committer {author} {START + c * STEP} +0000\n".encode("utf-8"))
        data(message)
        if c:
            stream.append(f"from :{c}\n".encode("utf-8"))
        changed = {}
        if c == 0:
            changed = {**{p: docs[p] for p in doc_paths}, **{p: sources[p] for p in source_paths}}
        else:
            doc = docs[doc_paths[c % FEATURES]]
            line = 2 + (c * 7) % (REQUIREMENTS_PER_FEATURE * LINES_PER_REQUIREMENT)
            if not doc[line].startswith("###") and doc[line]:
                doc[line] = doc[line].split(" #")[0] + f" #{c}"
            changed[doc_paths[c % FEATURES]] = doc
            for k in (c % len(source_paths), (c * 13) % len(source_paths)):
                sources[source_paths[k]].append(f"# change {c}")
                changed[source_paths[k]] = sources[source_paths[k]]
        for path, lines in changed.items():
            stream.append(f"M 100644 inline {path}\n".encode("utf-8"))
            data("\n".join(lines) + "\n")
    subprocess.run(["git", "init", "-q", "-b", "main", str(top)], check=True)
    subprocess.run(["git", "fast-import", "--quiet"], cwd=top, input=b"".join(stream), check=True)
    subprocess.run(["git", "checkout", "-q", "-f", "main"], cwd=top, check=True)
    rows = ["# AGNOS process index"]
    for path in doc_paths:
        rows.append(f"@{path}")
        rows.append(f"FTR-PRF-{doc_paths.index(path) + 1:03d}|1-{len(docs[path])}||Feature")
        f = doc_paths.index(path)
        for n in range(REQUIREMENTS_PER_FEATURE):
            first = 3 + n * LINES_PER_REQUIREMENT
            rows.append(f"{requirement_id(f, n)}|{first}-{first + LINES_PER_REQUIREMENT - 1}||Requirement {n}")
    (top / "process" / agnos_layout.INDEX).write_text("\n".join(rows) + "\n", encoding="utf-8")
    return top / "process", top / "src"


DRIVE = """
const out = document.documentElement.dataset;
const t0 = performance.now();
agnosTrace.showView("history");
out.draw = String(performance.now() - t0);
const plot = document.getElementById("history-plot");
const view = agnosTrace.historyView;
const times = [];
for (let i = 0; i < %d; i += 1) {
  const s = performance.now();
  if (i %% 3 === 0) plot.dispatchEvent(new WheelEvent("wheel", { deltaY: i %% 2 ? 100 : -100, clientX: view.xOf((view.span()[0] + view.span()[1]) / 2),
    clientY: plot.getBoundingClientRect().top + 60, bubbles: true, cancelable: true }));
  else if (i %% 3 === 1) plot.dispatchEvent(new KeyboardEvent("keydown", { key: i %% 2 ? "ArrowLeft" : "ArrowRight", bubbles: true }));
  else document.querySelector(`#history-kind [data-kind="${i %% 2 ? "all" : "agent"}"]`).click();
  times.push(performance.now() - s);
}
times.sort((a, b) => a - b);
out.p95 = String(times[Math.floor(times.length * %s)]);
out.rows = document.getElementById("history-rows").dataset.total;
""" % (STEPS, P95)


@unittest.skipUnless(PERF, "set AGNOS_PERF_CENTER_PERF=1 to measure the history (about a minute)")
class HistoryPerformanceTest(unittest.TestCase):
    """TASK-HST-007: RQ-HST-013."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp(prefix="agnos-history-perf-"))
        config = cls.folder / "gitconfig"
        config.write_text("", encoding="utf-8")
        cls.env = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(config), "GIT_CONFIG_NOSYSTEM": "1"})
        cls.env.start()
        cls.process, cls.sources = write_repository(cls.folder / "repo")

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        shutil.rmtree(cls.folder, ignore_errors=True)

    def generate(self, name, *extra):
        page = self.folder / name
        started = time.perf_counter()
        code, out, err = run_main(["--process", str(self.process), "--sources", str(self.sources), "--out", str(page),
                                   "--generated-at", "x", *extra])
        elapsed = time.perf_counter() - started
        self.assertEqual(0, code, err)
        return page, elapsed, page.with_suffix(".json").stat().st_size, out

    def test_RQ_HST_013_given_2000_commits_then_the_history_stays_within_its_time_size_and_drawing_budgets(self):
        self.generate("warm.html")                                  # the first run pays the imports and the disk cache
        _, plain_s, plain_bytes, _ = self.generate("plain.html")
        page, history_s, history_bytes, out = self.generate("history.html", "--history")
        added_s, added_bytes = history_s - plain_s, history_bytes - plain_bytes
        print(f"\nRQ-HST-013: {out.strip().split('; ')[-2]}; history adds {added_s:.2f} s and {added_bytes / 1024:.0f} KiB")
        self.assertIn(f"history: {COMMITS} commits, {HUMANS} humans, {len(AGENTS)} agents", out)
        self.assertLess(added_s, MAX_SECONDS)
        self.assertLess(added_bytes, MAX_BYTES)
        if BROWSER:
            got = dict(re.findall(r'data-(draw|p95|rows)="([^"]*)"', rendered_dom_after(page, DRIVE)))
            print(f"RQ-HST-013: History tab drawn in {float(got['draw']):.0f} ms, {got['rows']} rows; "
                  f"P95 of {STEPS} zoom, pan and filter steps {float(got['p95']):.1f} ms")
            self.assertLess(float(got["draw"]), MAX_DRAW_MS)
            self.assertLess(float(got["p95"]), MAX_STEP_MS)


if __name__ == "__main__":
    unittest.main()
