---
id: PL-DHJ7
title: The live ROADMAP sections carry about fifteen subset counts of the shape PL-GLBF checked, and unlike v0.2.8's those lists are still growing
priority: P3
effort: M
status: ready
classes: docs, infra
feature: dev-tooling
touches: ROADMAP.md, tools/doc_check.py
added: 2026-09-13
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_live_roadmap_subset_count_is_held_or_dated' tests/unit/test_doc_check.py
---

**Problem.** The live ROADMAP sections carry about fifteen subset counts of the shape PL-GLBF checked, and unlike v0.2.8's those lists are still growing

**Found 2026-09-13** working `PL-GLBF`, and deliberately left out of it: folding
this in would have turned an `S` item about three dead numbers in a shipped
section into an open-ended audit of the roadmap's live prose.

**Why the live ones are the real risk.** `PL-GLBF` established that its own
three examples cannot go stale — the v0.2.8 list is frozen and all ten ids it
names are closed. The same *shape* recurs about fifteen times in Gate 1's
declines and the Qt port's dispositions, and those lists are still growing with each
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
**Why it matters.** `PL-GLBF` (the ROADMAP subset counts are hand-maintained
and unchecked) rests on three numbers that cannot go stale, which is the
weakest case for the rule it establishes. These fifteen are the strong one:
they sit in Gate 1's declines and the Qt port's dispositions, both of which grow
with every triage pass - the 2026-09-13 pass added two paragraphs of exactly
that shape and moved a heading count by thirteen. A subset count that is wrong
is read as the project's own statement of what it owes, and `bin/docket wave`
prints the gate's computed numbers in every session digest beside these written
ones, with nothing telling a reader which kind they are looking at.

**Done when.** The decision above is recorded, and whichever kinds it covers
are handled: the decidable counts checked on the `PL-GLBF` pattern in
`tools/doc_check.py`, and the judgment ones either given a date so they read as
a record or left alone with that reasoning written where the next audit will
find it. The anchored kind needs nothing, and saying so explicitly is part of
the answer - otherwise the next pass re-examines it from scratch.

**Decided 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
The decision this item was holding is made, and it is the counts rule: a count
in prose is stated only where a check holds it to what it counts, or it is
dated. So the **decidable** counts gain checks on the `PL-GLBF` pattern, the
**judgment** counts are dated so they read as records under clause 4, and the
**anchored** kind needs nothing - which the item asked to have said explicitly,
so that the next audit does not re-examine it. Promoted from `needs-decision`
to `ready`, with a `verify:` command run on 2026-09-19 and watched to fail
(exit 1: the suite passes, the test it names does not exist yet).
