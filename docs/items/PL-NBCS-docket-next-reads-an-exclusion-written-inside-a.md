---
id: PL-NBCS
title: docket next reads an exclusion written inside a Required scope bullet as membership, so PL-B9PY is ranked in scope for v0.4.0 when ROADMAP.md sends it to Gate 1
status: untriaged
added: 2026-09-05
---

**Problem.** `bin/docket next product` ranks `PL-B9PY` (decompose
`SimulationView` so two runs can be rendered at once) second in the product
lane and marks it *"In scope for v0.4.0 - the teachable case, the step the
project is on."* `ROADMAP.md`'s v0.4.0 `Required scope` says the opposite, in
the bullet that names it:

> Stage 3, the `SimulationView` decomposition proper, is **not** in scope: it
> is queue item PL-B9PY and stays at Gate 1, because only v0.5.0's
> side-by-side comparison of two branches needs it (project owner,
> 2026-09-02).

Confirmed by parsing rather than inferred: `roadmap.parse_milestones` returns
`PL-B9PY` inside the v0.4.0 section's `scope_ids`, between `PL-WB0X` and
`PL-DHV7` - the position of the sentence that excludes it.

**Why it matters.** `docket next` is what every session reads before it picks
work, and `CLAUDE.md` forbids implementing beyond the current milestone. The
ranker currently tells each of them that Gate-1/v0.5.0 work is what v0.4.0 is
waiting on, stated as a fact and with the milestone named. That is the "gives a
wrong answer silently" test - the check passes while the guarantee it stands
for is void - in the one command the whole queue is read through.

`PL-D9WD` is placed by the same mechanism, from a passing mention in the
case-length time-base bullet. Harmless today because it is already `done`, but
it is the same read and it shows the mention/membership confusion is not a
one-off.

**Where.** `subprojects/docket/src/docket/roadmap.py` - `_subsection_ids` and
the `SECTION_ID_RE` reading, whose comment at `:335-349` already states the
trade deliberately:

> - the frozen list, by its entries' heads, because an entry is one bullet per
>   problem and an id later in the sentence is prose about another item;
> - `Required scope`, in full, because a milestone names what it covers in
>   whatever grammar the sentence wanted [...]

`PL-HDY6` fixed the frozen-list half by reading entry heads. The
`Required scope` half is read in full on purpose, and that is exactly what
makes an id named inside a scope bullet *to exclude it* read as membership.
`PL-6P9Y` covers the `### Explicitly out of scope for vX.Y.Z` heading, which is
a different structure and does not reach this case.

**The design question this poses**, and why it is not a one-line fix: the
comment's reasoning for reading `Required scope` in full is sound - a milestone
names its scope in whatever grammar the sentence wanted, so a head-only read
would lose `"(queue item PL-DHV7)"` mid-bullet. Candidate answers, none yet
chosen:

- read a bullet's ids only when the bullet does not carry an exclusion marker
  (`not in scope`, `stays at Gate`, `is **not**`), which is a grammar guess and
  the kind of judgment `CLAUDE.md` says not to script;
- have `ROADMAP.md` carry exclusions in `### Explicitly out of scope` only,
  never inside a scope bullet, and let `tools/doc_check.py` enforce that - the
  decidable half, and it moves the work out of the model permanently;
- report an id named in both a scope bullet and an exclusion as `ambiguous`
  rather than picking, so `docket next` prints no marking instead of a wrong
  one.

The second is the one to weigh first: it is a check rather than a heuristic,
and the safe direction to fail is already the reader's stated principle -
"an unread mention makes no claim, where an over-read one tells a session that
work the milestone excludes is the work the milestone is waiting on."

**Done when.** `bin/docket next` no longer reports `PL-B9PY` as in scope for
v0.4.0, and a test in `subprojects/docket/tests/test_roadmap.py` fixes the
behaviour against a section whose `Required scope` names an id in order to
exclude it.

**Found.** 2026-09-05, answering "what is left for 0.4.0". The reply that found
it had to override the ranker by hand.
