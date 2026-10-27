---
id: PL-DHJ7
title: The live ROADMAP sections carry about fifteen subset counts of the shape PL-GLBF checked, and unlike v0.2.8's those lists are still growing
priority: P3
effort: M
status: dropped
classes: docs, infra
feature: doc-consistency-checks
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-13
closed: 2026-10-27
reason: Gone, checked 2026-10-27: Gate 1's count paragraphs became records when v0.5.0 shipped, their sources moved onto item fields (PL-8QMD, PL-Z64T), and v0.7.0's live gate holds no count that is neither checked nor dated. The field checks the brief asked for would count a different set than the sentences do, so check_gate_counts' docstring now records why none is built.
verify: grep -q 'def test_a_live_roadmap_subset_count_is_held_or_dated' tests/unit/test_doc_check.py && uv run pytest tests/unit/test_doc_check.py
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

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** `check_gate_counts` at
`tools/doc_check.py:1504` still says "Prose is deliberately left alone", and
`git log -S'_withheld_counts' -- tools/doc_check.py` returns exactly one commit -
the original `PL-GLBF` pattern, with nothing built on it since. The count has
grown rather than held: the Gate 1 declines alone now carry roughly **35** bold
count paragraphs against the brief's "about fifteen", including two added
2026-09-19 (`ROADMAP.md:3218`, `:3395`). The decision half is recorded inside
this brief at `:66-74` and the item is `ready`; what is left is the whole
implementation.

**Checked 2026-10-27 against `origin/main` at `c95177a`, and dropped: the problem is gone, and the checks this brief asked for would count the wrong set.**

- **The fifteen to thirty-five paragraphs are records now.** They sat in
  Gate 1's declines, under v0.5.0. v0.5.0 shipped on 2026-09-21, so its
  section is a shipped release's section. `docs/MODEL.md`'s clause 4 makes
  every sentence in it a dated record. v0.6.0 shipped on 2026-10-20, so the
  same applies to Gate 2's prose.
- **What fed them was moved onto the items.** The per-pass prose subsections
  moved onto their items on 2026-09-23. A deferral became the
  `deferred-from:` field that `bin/docket wave` counts (`PL-8QMD`,
  2026-10-12). The lane groups were collapsed into one (`PL-Z64T`,
  2026-10-24). `docs/MODEL.md`'s counts rule (`PL-4FBP`, 2026-09-19) covers
  the rest.
- **The live gate holds no unchecked, undated count.** Every count in
  v0.7.0's section was read. Its two group headings are held by
  `check_gate_counts`. Every other count sits in a paragraph that carries its
  date ("Frozen 2026-10-25", "Swept for staleness on 2026-10-25"), or it
  names its ids beside it ("The four entries v0.6.0's gate deferred for item
  28", "its two other members, `PL-06LS` and `PL-XST1`").
- **Gate 2 wrote none of the kind either, over its whole life after the
  counts rule.** Its count sentences were "Thirteen entries were untriaged
  when this list was frozen", "Five entries are deferred to Gate 3", and
  "Four of the five are `safety`- or `science`-classed". The first is
  anchored to the freeze. The other two carry a date and a commit, and each
  names its ids.
- **The "decidable" kind turned out to be anchored.** Each such count is the
  ids of one decision at one commit, not a query over today's store. "Five
  entries are deferred to Gate 3" names `PL-WZVZ`, which now carries
  `deferred-from: v0.7.0`. Five of v0.6.0's entries still carry
  `deferred-from: v0.6.0`, but they include `PL-5B1N` in its place. So a
  field count would agree for the wrong reason. "Four of the five are
  `safety`- or `science`-classed" is five of five in today's store, since
  `PL-B396` gained `safety`. So a field count would fail a correct record.
  This is the near-miss field `PL-GLBF` warned about, one level up.
- **The judgment kind needs nothing new.** The counts rule already requires a
  date, and the writers have followed it.
- **The anchored kind needs nothing**, as this brief said. That conclusion,
  with the two worked examples above, is now written into
  `check_gate_counts`'s docstring in `tools/doc_check.py`. That docstring is
  where a session would build a check of gate prose, so the next audit finds
  the answer there.

The `verify:` command names a test that was never written, because no check
was built. A dropped item's command is printed by `bin/docket verify` and not
run (`PL-BX1C`).
