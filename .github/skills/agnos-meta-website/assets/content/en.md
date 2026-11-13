<!--
FTR-WEB-001: RQ-WEB-003 to RQ-WEB-012 / ADR-WEB-001: DEC-WEB-003. AGNOS website, English text.
Edit the words freely; keep the structure, then build again with the agnos-meta-website skill.
- "## <section>" opens a page element, "### <field>" one of its texts. Keep these ids identical in en.md and fr.md:
  the build refuses a field missing from one language, or unknown to the page template.
- A field is one paragraph, a list of "- " items, an index excerpt between two ``` lines (lines starting with @ are
  dimmed), or one image written as a linked image: [![alternative text](screens/<file>.png)](<address opened on click>)
- Inline: *emphasis*, **strong**, `code`, [link text](address). End a line with \ to force a line break.
- Comments like this one are ignored.
-->

## page

### title
AGNOS - Agentic efficiency by traceability

### description
AGNOS, a lightweight engineering process for AI-native development teams.

## notice

### label
Demo

### text
The views on this page come from Roombook, the AGNOS demo project, whose team and two months of history are simulated.

## brand

### name
AGNOS

### tagline
Agentic efficiency by traceability

## nav

### tour
The tour

### start
Get started

### demo
Demo

### sections
Sections

### language
Language

### english
EN

### french
FR

## hero

### kicker
Engineering process for agentic AI

### title
AI agents write the code, or much more.\
*You keep control.*

### text
AGNOS is a lightweight, tooled process for AI-native development teams (pods of a few people, or solo). Requirements, decisions, tasks, code and commits carry the same identifiers: the work stays explainable, and the process is measured on every project, in real time, with the built-in AGNOS Performance Center application.

### cta-demo
Open the demo Performance Center

### cta-tour
The tour

### tools
Works with Claude Code and GitHub Copilot (Codex support coming soon). Its artifacts are in Markdown, versioned in git, to maximise operational efficiency.

## chain

### title
One requirement, followed from need to commit

### mode-mixed
Mixed

### mode-on
End-to-end supervision

### in-loop
Human in the loop

### in-loop-text
The agent drafts; you decide and approve each step.

### on-loop
Human on the loop

### on-loop-text
The agent carries out the approved task; you supervise, and step in if needed.

### on-loop-draft-text
Asked to work in full autonomy, the agent drafts and takes the decisions; you supervise, and step in if needed.

### approve-on
Decisions delegated to the agent

### requirement
Requirement

### requirement-text
The expression of the need, formalised to be testable

### decision
Architecture and decision

### decision-text
Why this design, and what was ruled out

### task
Task

### task-text
Sized to the risk, approved before it starts

### approve
You approve

### code
Tests, then code

### code-text
Every element cites its identifiers

### done
Checklist passed

### commit
Commit

### commit-text
One per task, its identifiers checked by a script

### measure-text
End-to-end supervision of the process, across the whole project

### foot
Work is done in sessions: one functional area, one branch, ten tasks at most, for optimal context management

### supervision
Supervision

### requirement-id
RQ-BKG-003

### decision-id
DEC-BKG-002

### task-id
TASK-BKG-003

### code-id
OverlapRule.check

### commit-id
12dc6e4

### measure
Performance Center

### measure-id
Roombook

## tour

### eyebrow
The tour

### title
The Performance Center, the control centre for your agentic development

### text
The five views of the Performance Center meet the fundamental need to monitor your development.
Each example view below is a screenshot of the Performance Center on Roombook, the AGNOS demo project. Click one of them to open it, live, in the demo.

## labels

### see
What you see

### why
What makes it possible

### open
Open in the demo

## matrix

### view
Matrix

### question
Is what was asked for really built?

### see
The end-to-end traceability matrix, from functional capabilities to code, on a single page, directly exportable.

### why
Every element of the process is uniquely identified, from the functional capability to the commit. The specification and the tests, expressed in testable syntaxes (EARS, Gherkin), keep the agent's interpretation at implementation to a minimum.

### tags
- EARS
- Gherkin
- Identifiers in the code

### shot
[![The Matrix view of the Performance Center on Roombook](screens/matrix.png)](demo/PERF-CENTER.html#view=matrix)

### caption
Roombook: end-to-end traceability matrix.

## examples

### requirement
![A Roombook requirement, in EARS with its Gherkin criteria](screens/example-requirement.png)

### requirement-caption
Requirement RQ-BKG-003

### adr
![A Roombook architecture decision, with its diagram](screens/example-adr.png)

### adr-caption
ADR-BKG-001 and its diagram

### plan
![A Roombook plan, with one of its tasks](screens/example-plan.png)

### plan-caption
PLAN-BKG-001 and TASK-BKG-003

### zoom
Enlarged example

### close
Close

## graph

### view
Graph

### question
Why does this code exist, and what would a change touch?

### see
A requirement and everything attached to it: its feature, the decisions that shaped it, the tasks that delivered it, the files and functions that implement it.

### why
A single identifier grammar, written as comments in the documents, code, tests and commit messages. Each architecture decision has its own identifier: the code cites the exact decision it applies.

### tags
- Architecture decisions (ADR)
- One identifier grammar
- Identifiers in comments

### shot
[![The Graph view of the Performance Center, centred on requirement RQ-BKG-003](screens/graph.png)](demo/PERF-CENTER.html#RQ-BKG-003)

### caption
`RQ-BKG-003`, Double booking rejection, and everything that cites it.

## quality

### view
Quality

### question
Can we trust the way the process was applied?

### see
KPIs from A to E, computed from risk-weighted checks. Each gap points to the element to fix: on Roombook, functions that do not cite a requirement yet.

### why
Gates the agent cannot bypass. A task starts only once approved (Definition of Ready) and closes only once its checklist is passed (Definition of Done). Its tier, S, M or L, scales the formality to the risk of the change. A failing check is allowed one fix, then the agent stops and reports.

### tags
- Definition of Ready
- Definition of Done
- Tiers S, M, L

### shot
[![The Quality view of the Performance Center on Roombook](screens/quality.png)](demo/PERF-CENTER.html)

### caption
Roombook's report card, and the checks behind its grade.

## history

### view
History

### question
Who changed what, and when?

### see
Every change to a requirement, a decision, a file or a function, credited to its authors from git. Each identity is classed as human or AI agent, and each commit as human, agent or both together.

### why
One commit per task, made by a skill that writes the task and ADR identifiers into its message. Git remains the single system of record, independent of any infrastructure.

### tags
- One commit per task
- Human or agent

### shot
[![The History view of the Performance Center on Roombook](screens/history.png)](demo/PERF-CENTER.html)

### caption
Two months of development history of the Roombook application.

### note
Every commit, whether human, agentic or collaborative, can be traced through a requirement view or an implementation view.

## delivery

### view
Delivery

### question
What was delivered, and are we keeping potential agentic drift under control?

### see
The tasks delivered over time, weighted by their tier, and the friction of each session: questions the agent had to ask, error recoveries, re-tiered tasks, discrepancies caught at verification.

### why
Work is done in sessions of ten tasks at most, for optimal use of the context. Each session closes on its friction counters; if one of them is not zero, a self-improvement step proposes rules for the project, applied once approved and within a defined budget.

### tags
- Sessions
- Friction counters
- Self-improvement

### shot
[![The Delivery view of the Performance Center on Roombook](screens/delivery.png)](demo/PERF-CENTER.html)

### caption
What Roombook delivered, period by period.

## more

### eyebrow
Behind the views

### title
Three more reasons why it holds at scale

## index-card

### title
Designed for agents: the index

### text
A script indexes every artifact, one line each, with its exact location. The agent reads this small file first and opens only the useful lines. It takes the next free identifier from it: none is ever duplicated. The Performance Center reads the same index: what the agent sees and what you measure cannot diverge. The index is recomputed automatically, at the start of every session and before every commit, by a deterministic skill.

### caption
Roombook: an excerpt of the index.

### excerpt
```
@agnos-process/1.requirements/FTR-BKG-001-room-reservation.md
RQ-BKG-003|42-56||Double booking rejection
@agnos-process/3.plan/PLAN-BKG-001-core-booking.md
TASK-BKG-003|50-66|Done|Implement overlap rule
```

## id-card

### title
Exact links, not resemblances

### text
Every requirement, decision, task and function carries a unique identifier, and each element cites those it depends on, like a primary key and its foreign keys in a database. The agent therefore follows exact links instead of guessing, by semantic proximity, which text relates to what. The same inputs give the same links: the agent's work becomes more deterministic, and verifiable.

### foreign-key
Foreign key

### cites
cites

### primary-key
Primary key

### requirement
```
### RQ-BKG-003: Double booking rejection
```

### task
```
### TASK-BKG-003: Implement overlap rule
- Requirement refs: ==RQ-BKG-003==
- ADR refs: ADR-BKG-001 (DEC-BKG-002)
```

### adr
```
# ADR-BKG-002: Initial reservation storage
Motivated by: RQ-BKG-002, ==RQ-BKG-003==, RQ-BKG-005 (FTR-BKG-001); builds on ADR-BKG-001.
### DEC-BKG-003: In-memory dictionary for reservations
```

### semantic
Semantic matching: a probable link

### exact
Identifier: an exact link

### code
```
@service/roombook/rules/overlap_rule.py
# ==RQ-BKG-003==, DEC-BKG-002 (ADR-BKG-001)
class OverlapRule:
    """Rejects an interval that overlaps an existing reservation (==RQ-BKG-003==)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise ReservationConflict naming the first overlapping reservation (==RQ-BKG-003==)."""
```

### graph
TASK-BKG-003, ADR-BKG-002 and overlap_rule.py all cite RQ-BKG-003

### task-id
TASK-BKG-003

### requirement-id
RQ-BKG-003

### adr-id
ADR-BKG-002

### requirement-title
Double booking rejection

### task-title
Implement overlap rule

### adr-title
Initial reservation storage

### file-id
overlap_rule.py

### file-title
OverlapRule


## design-card

### title
Interfaces under the same control

### text
A project with an interface defines its design system before its first screen, as a requirement and an architecture decision. The screens cite it, and the code reads every colour and every size from a token. On Roombook, a test rejects any raw value.

### primary-name
Primary

### primary-tokens
```
button.primary.background
→ colour.accent.default
→ colour.blue.600 = ==#2563eb==
```

### primary-css
```
.button-primary {
  background: var(--button-primary-background);
  color: var(--button-primary-text);
}
```

### primary-button
Book this room

### danger-name
Danger

### danger-tokens
```
button.danger.background
→ colour.error.strong
→ colour.red.700 = ==#b91c1c==
```

### danger-css
```
.button-danger {
  background: var(--button-danger-background);
  color: var(--button-danger-text);
}
```

### danger-button
Cancel this reservation

### caption
A button's background, in Roombook's tokens: `FTR-DSN-001` and `ADR-DSN-001`.

## close

### title
See it on a real project

### text
The demo page contains all the views, all the links and all the commits of Roombook's two simulated months.

### address
Generated by agnos-perf-center on Roombook, and published with this site.

### cta
Open the demo Performance Center

## start

### title
Three steps to the first session

### step1-title
Install the plugin

### step1-text
A single marketplace for Claude Code, GitHub Copilot and OpenAI Codex.

### step2-title
Add AGNOS to a project

### step2-text
One call to `agnos-init`. Your own files remain intact.

### step3-title
Start a session

### step3-text
In a new conversation, the agent records the session and opens its branch.

## footer

### developers
[For your developers: the documentation on GitHub](https://github.com/spashx/agnos-lightweight-process)

### license
AGNOS is distributed under the GNU Affero General Public License v3.
