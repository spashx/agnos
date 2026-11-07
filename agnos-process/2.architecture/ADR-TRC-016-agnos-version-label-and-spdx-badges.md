# ADR-TRC-016: One "AGNOS v.<major>.<minor>" Label, and Licence Badges Linking to SPDX

## Status
Accepted (owner, 2026-11-07) — for RQ-TRC-109, RQ-TRC-110, RQ-TRC-111, RQ-TRC-112, RQ-TRC-116. DEC-TRC-061 amends DEC-TRC-057 and
DEC-TRC-059; DEC-TRC-062 amends DEC-TRC-058.

## Context
The foot of the left panel reads "AGNOS Performance Center v.3.1" (DEC-TRC-057) while the About lockup names "AGNOS" alone
(DEC-TRC-059): two names for one application, and the version absent where the reader learns who made the page. The Licenses topic
opens with a sentence explaining badges the reader sees anyway, and its badges are not links, except the application's, which opens
the repository's licence text (DEC-TRC-058). Owner requests of 2026-11-07.

## Decision

### DEC-TRC-061: The foot and the About name both read "AGNOS @APP_VERSION@"
The template's foot becomes "AGNOS @APP_VERSION@", and the About name beside the mark "AGNOS @APP_VERSION@": the generator replaces
both markers with the same `v.<major>.<minor>` read from `VERSION.txt` (DEC-PLG-032), or with nothing, leaving "AGNOS". The name keeps
its style and tokens of DEC-TRC-059 (30 px, weight 700, line height 1.1, letter-spacing 0.12 em). Amends DEC-TRC-057 on the foot's
text and DEC-TRC-059 on the name's text. Fulfils RQ-TRC-109, RQ-TRC-110, RQ-TRC-116.

### DEC-TRC-062: Each licence badge links to its SPDX page; the introduction sentence goes
Every badge of the Licenses topic, the application's included, is an `<a>` opening `https://spdx.org/licenses/<id>.html` in a new tab
(`target="_blank"`, `rel="noopener"`), the address built from one named template constant and the licence's SPDX identifier. Only a
licence of the script's tone table gets a link; each address of that table was checked to answer HTTP 200 when the task was done.
A licence outside the table keeps its badge without a link (the existing test already fails on such a licence). No request is made at
generation or load, so RQ-TRC-080 holds. The sentence "The licence of this application, and of each library … in a new tab." is
removed. Amends DEC-TRC-058 on the application badge's link. Fulfils RQ-TRC-111, RQ-TRC-112.

## Consequences
- Easier: one name for the application; the version shows in About; a licence is one click from its reference text.
- Harder: a licence added to the table needs its SPDX address checked once.
- Constrained: the application badge no longer opens the repository's own `LICENSE`.

## Alternatives Considered
- **Check SPDX at generation or in the tests**: the generator works offline and the tests would depend on the network. Rejected.
- **Keep the application badge on the repository's `LICENSE`**: two kinds of destination for one kind of badge. Rejected (owner, 2026-11-07).
- **A second, smaller version line below the About name**: the owner asked for the same label, in the name's style. Rejected.

## Diagram
```mermaid
flowchart LR
    V[VERSION.txt] -->|v.major.minor| G[perf_center.py]
    G -->|@APP_VERSION@| F[Foot: AGNOS v.3.1]
    G -->|@APP_VERSION@| A[About name: AGNOS v.3.1]
    T[tone table by licence] --> B[badge a href=spdx.org/licenses/ID.html]
```
