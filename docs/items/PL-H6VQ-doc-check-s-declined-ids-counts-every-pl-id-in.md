---
id: PL-H6VQ
title: doc_check's _declined_ids counts every PL- id in a Declined-to-Gate subsection, including ids the deferral's prose only cites, so an item mentioned in another item's reasoning reads as disposed and check_gate_dispositions goes silent on it
priority: P2
effort: S
status: done
classes: defect, infra
feature: gate-list-integrity
milestone: v0.5.1
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-20
closed: 2026-09-21
pr: 852
payoff: an open debt item cited in another item's reasoning stops reading as disposed, so the gate check goes quiet only for items that actually have a disposition
verify: grep -q 'def test_a_group_deferral_naming_its_ids_only_in_prose_is_read' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _declined_ids counts every PL- id in a Declined-to-Gate subsection, including ids the deferral's prose only cites, so an item mentioned in another item's reasoning reads as disposed and check_gate_dispositions goes silent on it

**Found 2026-09-20 while closing `PL-82B0`**, which fixed the adjacent defect
(only the first subsection was read) and left this one untouched deliberately:
it is a different question about the same function and wanted its own item.

**Where.** `tools/doc_check.py`'s `_declined_ids`, the
`re.findall(r"PL-[A-Z0-9]{4}", ...)` over each subsection's whole text.

**Measured 2026-09-20.** The one `### Declined to Gate ...` subsection in
`ROADMAP.md` holds 103 `- PL-` entry lines and mentions 385 distinct ids across
its prose. Every one of those 385 is returned as deferred, so an id a deferral
merely cites - as a cause, a precedent, or the item a ground was argued from -
is counted as having a recorded disposition it does not have.

**Why it matters, and why the direction is the safe one.** `PL-HJZW` made a
missing disposition a hard error rather than an advisory, so an id wrongly read
as disposed makes the check go quiet rather than fail: the failure mode is an
item silently escaping the gate's disposition rule, not a false red. That is
the safer direction and still a silent wrong answer, which is the shape
`CLAUDE.md` names first among its compounding-friction tests.

**Not urgent, and here is why.** The over-broad read only matters for an id
that is *open debt* and cited in the subsection without an entry of its own.
Nobody has counted how many that is; that count is the first thing to run, and
it decides whether this is a real gap or a theoretical one.

**Done when.** The count above has been run; and either `_declined_ids` reads
only the entry lines - `^- PL-XXXX` - with the prose left to explain rather than
to dispose, or the item records why reading the prose is right.


## Closed 2026-09-21 on the second disposition: the prose read is right

**The count, run against v0.5.0's two `### Declined to Gate ...` subsections** —
the last pair this project has written, 1,577 lines, read with the store as it
stood on 2026-09-21. They name **433 distinct ids**, all 433 of which
`_declined_ids` returns. **169 are open debt**, which is the only population
the over-read can silence. Of those 169: **67** have an entry line of their
own, **5** lead a disposition paragraph, and **97 are named only inside a
paragraph's body**.

**Those 97 are not citations.** Every one sits in a *group deferral* — a
paragraph that states a ground and then enumerates the ids it covers:
"**16 sit wholly in the workflow lane**: `PL-0HPV`, `PL-0PJG`, …", "The full 9:
…", "**Seventeen from the 2026-09-19 triage pass**". A prose paragraph is this
section's form for deferring a group exactly as an entry line is its form for
deferring one item. So the narrowing this item proposed — read only
`^- PL-XXXX` — would have converted **97 recorded dispositions into hard
errors**.

**And the citation half measures zero.** 42 distinct ids are cited inside
another entry's own line, which is where "an item mentioned in another item's
reasoning" actually sits, because an entry line carries the item's title and a
title routinely names the item it is about. Not one of the 42 is an open debt
item lacking a disposition: **37 are closed**, 3 carry no debt class, and the
two that are open debt — `PL-G8TR` and `PL-QV5Y` — each carry an entry of their
own. That is structural rather than lucky: a citation points at a *cause*, and
a cause is historical, so it is usually closed by the time a deferral cites it.

**So the `payoff:` above was not delivered and could not be — there was nothing
to buy.** The count the item asked for is what says so, which is why it asked
for it first.

**What landed.** No behaviour change. `_declined_ids`' docstring now records
the measurement and the refusal, so the next session that has this idea reads
the count instead of re-deriving it, and
`test_a_group_deferral_naming_its_ids_only_in_prose_is_read` pins the decision.
The test earns its place on a timing argument rather than a taste one: the
current gate (v0.6.0) carries **no** `### Declined to Gate ...` subsection at
all, so the narrowing passes `make check` on the day it lands — verified by
applying it and watching the suite and `tools/doc_check.py check` both stay
green — and would break only when the next gate wrote its first group deferral.
Without the test that failure arrives months later with no author present.

**The residual, accepted rather than overlooked.** An open debt id cited here
and disposed of nowhere would still go silent. No read of the document can
catch it: separating a citation from a disposition is the judgment half
`CLAUDE.md` declines to script. It measures zero today, and the direction stays
the safe one — quiet rather than a false red.

**Found while measuring, filed separately:** `DECLINED_HEADING_RE` matches only
`### Declined to Gate`, and `ROADMAP.md` records dispositions under two other
headings as well — `### Deferred to v0.4.26, …` and `### Sequenced past v0.5.0,
…`, the latter naming two open debt items. That is the same function reading
too *little*, and it fails toward a false red rather than silence.
