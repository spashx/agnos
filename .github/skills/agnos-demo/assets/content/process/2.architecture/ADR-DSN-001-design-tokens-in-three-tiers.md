# ADR-DSN-001: Design tokens in three tiers, generated as CSS custom properties

<!-- Motivated by: RQ-DSN-001 to RQ-DSN-005 (FTR-DSN-001); design system required by MANDATORY DESIGN SYSTEM -->

## Status
Accepted

## Context
The web interface needs a design system before its first screen: one source of truth for every visual value,
readable by code without a browser, that keeps a screen from slipping a raw colour or size into its markup.
The stack is Node with erasable TypeScript and no runtime dependency.

## Decision

### DEC-DSN-001: One JSON token file with three tiers, loaded and checked headlessly
All visual values live in `client/design/tokens.json`: global tokens hold the raw values, semantic tokens
alias a global token, component tokens alias a semantic token (RQ-DSN-001, RQ-DSN-002). A TypeScript module
loads the file with no window or browser, resolves alias chains, rejects a token that breaks the tier chain
and checks the contrast ratio of the text and background pairings declared in the file (RQ-DSN-004).

### DEC-DSN-002: Stylesheet generated at serve time from `var()` references only
The stylesheet is generated from the tokens, never written by hand: a `:root` rule exposes every token as a
custom property, aliases kept as `var()` references to the tier below, then the component rules use only
`var()` (RQ-DSN-003). A unit test scans the interface sources for hexadecimal colours, colour functions and
dimensions, so a raw literal fails the test run (RQ-DSN-005).

## Consequences
- A value changes in one place; the generated stylesheet and every test read the same file.
- The chain is checked by tests, not by review alone; a token added in the wrong tier fails immediately.
- The class names shared by views and stylesheet are declared once, so a selector cannot drift from its markup.
- Server-side generation means the browser needs no build step, at the price of one more request for the CSS.

## Alternatives Considered
- Tokens authored directly in a hand-written CSS file: rejected, not readable by tests or other tools and
  the tiers cannot be checked.
- A token tool such as Style Dictionary: rejected, an npm dependency and a build step for about 150 tokens.
- Styles written in the TypeScript views (inline styles): rejected, it spreads values over the views and
  makes the literal check harder.

## Diagram
```mermaid
flowchart LR
  TJ[tokens.json: global, semantic, component] --> TS[Token module: resolve, tiers, contrast]
  TS --> SS[Stylesheet generator: custom properties and component rules]
  SS -->|/styles.css| BR[Browser]
  TJ -.-> TST[Tests: tier chain, contrast, literal scan]
```
