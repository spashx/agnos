# The graph file

<!-- RQ-TRC-129, RQ-TRC-130, RQ-TRC-133 / ADR-TRC-022 (DEC-TRC-074, DEC-TRC-075) -->

`agnos-process/4.knowledge/agnos-graph.json` by default: one JSON document, keys sorted and no indentation, so that two runs on
the same inputs and the same `--generated-at` write the same bytes. It holds the state of the project at its date and commit,
never a judgement of it: no coverage, finding nor score (those are the performance center's). A reader rejects a file that is
not JSON or that holds no `elements` list.

| Key | Content |
|---|---|
| `meta` | When and how the state was read, below |
| `elements` | One object per ID: those the index defines, in index order, then the undefined ones by name |
| `edges` | `[source, target, kind, proofs]`, sorted; `kind` is `contains` (a range holding another), `refs` (a line of a document citing an ID) or `code` (a line of a source file citing an ID); `proofs` is a list of `[line, text]`, empty for `contains` |
| `files` | `{path, ids}` per scanned source file, by path; `ids` counts its `code` links |
| `tasks` | `{TASK-ID: {tier, requirements}}`: `tier`, `S`, `M`, `L` or null, read from the task's lines, and `requirements`, the requirement IDs it cites |
| `callGraph` | With `--call-graph` and tree-sitter installed: the performance center's call graph block, plus `parsedFiles` and `unparsedFiles`, the paths read and those that did not parse |
| `history` | With `--history` in a git repository: who worked on each element and on the code, per commit |
| `delivery` | With `--history`: the delivered tasks and the identities' active days |

## `meta`

| Key | Content |
|---|---|
| `generatedAt` | The state's date, `YYYY-MM-DDTHH:MMZ`, UTC |
| `commit` | The HEAD commit of the repository holding the process folder, or null outside git |
| `process`, `sources` | The folders read, as given |
| `extensions`, `names`, `excludes` | The scan lists in effect: the extensions scanned, the file names always scanned, the patterns skipped |
| `summaries` | `{callGraph, history}`: the summary line's parts for the call graph and the history, when asked; `callGraph` also says when tree-sitter was missing |

## An element

| Key | Content |
|---|---|
| `id`, `type`, `tri` | `RQ-ABC-001`, `RQ`, `ABC` |
| `kind` | `element` (the index defines it) or `undefined` (only cited) |
| `doc`, `first`, `last` | The document and the line range the index gives; empty and 0 for an undefined ID |
| `status`, `title` | As the index gives them |

The call graph, history and delivery blocks have the format the performance center's page reads; their keys are listed in
`agnos-perf-center/references/data-format.md`.
