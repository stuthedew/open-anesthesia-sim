---
id: PL-DHJ7
title: The live ROADMAP sections carry about fifteen subset counts of the shape PL-GLBF checked, and unlike v0.2.8's those lists are still growing
status: untriaged
added: 2026-09-13
---

**Problem.** The live ROADMAP sections carry about fifteen subset counts of the shape PL-GLBF checked, and unlike v0.2.8's those lists are still growing

**Found 2026-09-13** working `PL-GLBF`, and deliberately left out of it: folding
this in would have turned an `S` item about three dead numbers in a shipped
section into an open-ended audit of the roadmap's live prose.

**Why the live ones are the real risk.** `PL-GLBF` established that its own
three examples cannot go stale — the v0.2.8 list is frozen and all ten ids it
names are closed. The same *shape* recurs about fifteen times in Gate 1's
declines and v0.5.1's dispositions, and those lists are still growing with each
triage pass, so they genuinely can drift.

**They do not want one answer.** Sampling shows three kinds:

- **Decidable from a field already there** — "Four further `safety`/`science`
  items" is a query over `classes:`; "Four are waiting on the port" is a query
  over `blocked-by:`. These are checkable on the `PL-GLBF` pattern.
- **Already anchored in time** — "Eleven more from the 2026-09-12 triage pass",
  "Three more from the `vcs.py` batch closure". A record of what a pass found on
  a date cannot go stale, for the same reason a shipped section cannot, and the
  roadmap already uses this convention deliberately elsewhere ("those headings
  record what the list said on 2026-09-06 rather than a claim about today").
- **Judgment** — "Four are the specification disagreeing with the tree it
  describes", "Two are decisions this gate should not force". No field decides
  these, and `PL-GLBF` measured why the nearest one cannot be pressed into
  service: `touches:` records the files an entry expects to change, not the
  scope it is permitted to reach, and on `PL-GLBF`'s own example the two
  disagree (2 against 3).

**Decision needed.** Whether the first kind gains checks on the `PL-GLBF`
pattern, and whether the third kind is required to carry a date so it reads as a
record rather than a live claim. The second kind needs nothing.

**Where.** `ROADMAP.md`, the sections from Gate 1's declines onward;
`tools/doc_check.py`'s `check_gate_counts`.
