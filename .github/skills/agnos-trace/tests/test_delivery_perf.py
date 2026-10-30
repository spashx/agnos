"""Measure of the delivery's speed and size (RQ-TRC-078, TASK-TRC-062), on a generated repository of 1,000 tasks, each
delivered (its status turned to Done) in a commit of its own, by six identities.

Run from the repository root with AGNOS_TRACE_PERF=1: python -m unittest discover -s .github/skills/agnos-trace/tests -p test_delivery_perf.py -v
The repository is written in one `git fast-import`, with an empty global git configuration.
"""
import json
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
sys.path.insert(0, str(HERE))

import trace_matrix as tm  # noqa: E402
from test_trace_matrix import BROWSER, rendered_dom_after, run_main  # noqa: E402

PERF = os.environ.get("AGNOS_TRACE_PERF") == "1"
TRIGRAMS = [f"PR{chr(ord('A') + n)}" for n in range(10)]
TASKS_PER_PLAN = 100                                # 10 plans of 100 tasks: 1,000 tasks
TASK_LINES = 5
TIERS = ("S", "M", "L")
PEOPLE = ("Dev 1 <dev1@example.com>", "Dev 2 <dev2@example.com>", "Dev 3 <dev3@example.com>",
          "Claude Opus 5.5 <noreply@anthropic.com>", "Claude Sonnet 5.5 <noreply@anthropic.com>", "Codex <codex@openai.com>")
SOURCES = 200
START = 1767225600                                  # 2026-01-01, UTC
STEP = 3600                                         # a delivery every hour: 1,000 hours, about six weeks
MAX_SECONDS = 2                                     # RQ-TRC-078's metrics
MAX_BYTES = 300 * 1024
MAX_DRAW_MS = 300
MAX_STEP_MS = 100
P95 = 0.95
STEPS = 50


def plan_lines(tri, done):
    lines = [f"# PLAN-{tri}-001: Plan", ""]
    for n in range(TASKS_PER_PLAN):
        status = "Done" if (tri, n) in done else "Not Started"
        lines += [f"### TASK-{tri}-{n + 1:03d}: Task {n + 1}", f"- **Tier**: {TIERS[n % len(TIERS)]}", f"- **Status**: {status}",
                  "- **Requirement refs**: None", ""]
    return lines


def write_repository(top):
    """The repository and its process index; returns the process and source folders."""
    sources = {f"src/f{n:03d}.py": ["def run():", "    return 0"] for n in range(SOURCES)}
    tasks = [(tri, n) for n in range(TASKS_PER_PLAN) for tri in TRIGRAMS]
    done = set()
    stream = []

    def data(text):
        raw = text.encode("utf-8")
        stream.append(f"data {len(raw)}\n".encode("utf-8") + raw + b"\n")

    def commit(c, author, message, changed):
        stream.append(f"commit refs/heads/main\nmark :{c + 1}\nauthor {author} {START + c * STEP} +0000\n"
                      f"committer {author} {START + c * STEP} +0000\n".encode("utf-8"))
        data(message)
        if c:
            stream.append(f"from :{c}\n".encode("utf-8"))
        for path, lines in changed.items():
            stream.append(f"M 100644 inline {path}\n".encode("utf-8"))
            data("\n".join(lines) + "\n")

    commit(0, PEOPLE[0], "docs: plans", {**{f"process/3.plan/PLAN-{t}-001.md": plan_lines(t, done) for t in TRIGRAMS}, **sources})
    for c, (tri, n) in enumerate(tasks, 1):
        done.add((tri, n))
        source = f"src/f{c % SOURCES:03d}.py"
        sources[source].append(f"# change {c}")
        commit(c, PEOPLE[c % len(PEOPLE)], f"{'fix' if c % 7 == 0 else 'feat'}({tri}): TASK-{tri}-{n + 1:03d} done",
               {f"process/3.plan/PLAN-{tri}-001.md": plan_lines(tri, done), source: sources[source]})
    subprocess.run(["git", "init", "-q", "-b", "main", str(top)], check=True)
    subprocess.run(["git", "fast-import", "--quiet"], cwd=top, input=b"".join(stream), check=True)
    subprocess.run(["git", "checkout", "-q", "-f", "main"], cwd=top, check=True)
    rows = ["# AGNOS process index"]
    for tri in TRIGRAMS:
        rows += [f"@process/3.plan/PLAN-{tri}-001.md", f"PLAN-{tri}-001|1-{2 + TASKS_PER_PLAN * TASK_LINES}||Plan"]
        rows += [f"TASK-{tri}-{n + 1:03d}|{3 + n * TASK_LINES}-{2 + (n + 1) * TASK_LINES}|Done|Task {n + 1}" for n in range(TASKS_PER_PLAN)]
    (top / "process" / "INDEX.idx.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return top / "process", top / "src"


DRIVE = """
const out = document.documentElement.dataset;
const t0 = performance.now();
agnosTrace.showView("delivery");
out.draw = String(performance.now() - t0);
const times = [];
const presets = document.getElementById("delivery-preset-b");
for (let i = 0; i < %d; i += 1) {
  const s = performance.now();
  if (i %% 4 === 0) document.querySelector(`#delivery-tiers [data-tier="${["S", "M", "L"][i %% 3]}"]`).click();
  else if (i %% 4 === 1) document.querySelector(`#delivery-kinds [data-kind="${i %% 2 ? "agent" : "human"}"]`).click();
  else if (i %% 4 === 2) document.querySelector(`#delivery-grain [data-grain="${i %% 3 ? "week" : "day"}"]`).click();
  else { presets.value = i %% 3 ? "previous-14" : "previous-7"; presets.dispatchEvent(new Event("change")); }
  times.push(performance.now() - s);
}
times.sort((a, b) => a - b);
out.p95 = String(times[Math.floor(times.length * %s)]);
out.rows = String(agnosTrace.delivery.rows.length);
""" % (STEPS, P95)


@unittest.skipUnless(PERF, "set AGNOS_TRACE_PERF=1 to measure the delivery (about a minute)")
class DeliveryPerformanceTest(unittest.TestCase):
    """TASK-TRC-062: RQ-TRC-078."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp(prefix="agnos-delivery-perf-"))
        config = cls.folder / "gitconfig"
        config.write_text("", encoding="utf-8")
        cls.env = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(config), "GIT_CONFIG_NOSYSTEM": "1"})
        cls.env.start()
        cls.process, cls.sources = write_repository(cls.folder / "repo")

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        shutil.rmtree(cls.folder, ignore_errors=True)

    def generate(self, name):
        page = self.folder / name
        started = time.perf_counter()
        code, out, err = run_main(["--process", str(self.process), "--sources", str(self.sources), "--out", str(page),
                                   "--generated-at", "x", "--history"])
        elapsed = time.perf_counter() - started
        self.assertEqual(0, code, err)
        return page, elapsed

    def test_RQ_TRC_078_given_1000_delivered_tasks_then_the_delivery_stays_within_its_time_size_and_drawing_budgets(self):
        self.generate("warm.html")                                  # the first run pays the imports and the disk cache
        with mock.patch.object(tm, "task_tiers", return_value=None):  # the same history, without the delivery
            _, without_s = self.generate("without.html")
        page, with_s = self.generate("delivery.html")
        data = json.loads(page.with_suffix(".json").read_text(encoding="utf-8"))
        added_s = with_s - without_s
        added_bytes = len(tm.embed_json(data["delivery"]).encode("utf-8"))
        counted = sum(1 for row in data["delivery"]["tasks"] if row[7] is None)
        print(f"\nRQ-TRC-078: {len(data['delivery']['tasks'])} tasks delivered ({counted} counted); the delivery adds "
              f"{added_s:.2f} s and {added_bytes / 1024:.0f} KiB")
        self.assertEqual(len(TRIGRAMS) * TASKS_PER_PLAN, counted)
        self.assertLess(added_s, MAX_SECONDS)
        self.assertLess(added_bytes, MAX_BYTES)
        if BROWSER:
            got = dict(re.findall(r'data-(draw|p95|rows)="([^"]*)"', rendered_dom_after(page, DRIVE)))
            print(f"RQ-TRC-078: Delivery tab drawn in {float(got['draw']):.0f} ms, {got['rows']} tasks; "
                  f"P95 of {STEPS} filter, grain and period changes {float(got['p95']):.1f} ms")
            self.assertLess(float(got["draw"]), MAX_DRAW_MS)
            self.assertLess(float(got["p95"]), MAX_STEP_MS)


if __name__ == "__main__":
    unittest.main()
