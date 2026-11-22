# agnos-perf-center: maintaining the skill

<!-- RQ-TRC-099, DEC-TRC-051. Libraries: FTR-TRC-005, ADR-TRC-010; design system: ADR-TRC-002. -->

## Generator details

- The page is made from the graph file of `agnos-graph` alone <!-- RQ-TRC-131, DEC-TRC-075 -->; the scan options are passed to
  `agnos-graph` when the graph is absent or `--rebuild` is given, and its `--help` gives their default lists. <!-- RQ-TRC-119, RQ-TRC-132 -->
- Exit code 1: a graph absent with no `--sources`, a graph file that is not JSON or holds no `elements`, a graph `agnos-graph`
  could not build (its own message precedes), or a broken design token.
- Without the call-graph packages, the summary says `call graph skipped: tree-sitter not installed, run: pip install -r …`. They
  are prebuilt wheels, no compiler needed.
- `--history-since` and `--history-depth` apply together. `no history: <cause>` means git is missing, the process folder is in
  no git working tree, or the repository has no commit.

## Tests

Running them needs Python 3.10 or later. `python -m unittest discover -s <this skill's folder>/tests -v`; they load the modules of
the sibling `agnos-graph` skill, whose own tests check the graph, the call graph and the history <!-- RQ-TRC-133 -->: a synthetic process in
`tests/fixtures/repo` plants one element of every finding. The page tests run in a headless Chromium-family browser (Edge,
Chrome, Chromium; `AGNOS_PERF_CENTER_BROWSER=<path>` to choose) and are skipped when none is found. The call-graph tests
(`tests/fixtures/repo/calls`) are skipped without the tree-sitter packages; `AGNOS_PERF_CENTER_PERF=1` adds the measure on a
generated tree of 20,000 functions and 100,000 calls (about a minute), and the measures of the history (`test_history_perf.py`,
2,000 commits) and of the delivery (`test_delivery_perf.py`, 1,000 tasks delivered). <!-- RQ-TRC-078 -->

## Libraries <!-- FTR-TRC-005; ADR-TRC-010: DEC-TRC-040, DEC-TRC-041 -->

The page loads Cytoscape.js (the Graph view) and Apache ECharts (the library charts) from `cdnjs.cloudflare.com`, at the
versions recorded in `assets/libraries.json` with their integrity hash <!-- RQ-TRC-080, RQ-TRC-082 -->; nothing is copied into
the skill or the page. The page needs the network once; the browser's cache usually serves the libraries afterwards.
Without them, the views that need them say so and the others work <!-- RQ-TRC-081 -->. To change a version: change its
version, URL and `integrity` together in `libraries.json` (the hash the cdnjs API publishes,
`https://api.cdnjs.com/libraries/<name>/<version>?fields=sri`), then run the tests, which need the network: without
cdnjs, the page tests are skipped.

## Brand, version and licences <!-- FTR-TRC-009; ADR-TRC-014: DEC-TRC-056 to DEC-TRC-058 -->

The brand mark is one symbol of the template (`brand-mark`), coloured by the `brand-*` tokens <!-- RQ-TRC-114 -->; the About
topic shows it large with the name "AGNOS v.<major>.<minor>" and the tagline beside it, set by the tokens `text-wordmark`, `tracking-wordmark`,
`tracking-tagline`, `line-display` and `line-snug` <!-- RQ-TRC-116 -->. The foot of
the left panel shows "AGNOS v.<major>.<minor>" <!-- DEC-TRC-061 -->, the version read at each generation from `agnos-init/assets/templates/VERSION.txt`, a file of the
sibling skill; absent or not one SemVer line, it shows the title alone <!-- RQ-TRC-109, RQ-TRC-110 -->. The Help dialog's Licenses
topic draws the application's licence and each library of `libraries.json` as badges <!-- RQ-TRC-111, RQ-TRC-112 -->: the tone of
a licence is its entry in `LICENCE_TONE` of `matrix.js` (any other licence takes the light tone), and a test fails when a
library's licence has none, so classify a new licence when adding a library. A badge of a tabled licence links to
`https://spdx.org/licenses/<id>.html`: check once that the new licence's address answers HTTP 200 <!-- DEC-TRC-062 -->.

## Design system

Every colour, size and duration of the page is a token of `assets/tokens.json` (global → semantic → component); the CSS
and the script use only the `--s-*` and `--c-*` custom properties the generator writes from it. Change a value there,
never in `matrix.css` or `matrix.js` (a test fails on any raw colour, `px` or `ms` in them).
