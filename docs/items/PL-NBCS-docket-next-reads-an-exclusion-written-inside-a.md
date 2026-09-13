---
id: PL-NBCS
title: docket next reads an exclusion written inside a Required scope bullet as membership, so PL-B9PY is ranked in scope for v0.4.0 when ROADMAP.md sends it to Gate 1
priority: P2
effort: M
status: done
classes: defect
touches: ROADMAP.md, subprojects/docket/README.md, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py, tools/doc_check.py, tests/unit/test_doc_check.py
verify: uv run pytest subprojects/docket/tests/test_roadmap.py && grep -q 'def test_an_id_a_scope_bullet_names_only_to_exclude_it' subprojects/docket/tests/test_roadmap.py
added: 2026-09-05
closed: 2026-09-13
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

**Decision needed.** The design question this poses, and why it is not a
one-line fix: the
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

## Decided 2026-09-13: the second candidate — the exclusion moves, and a check holds it there

**First, the reported symptom no longer reproduces, and the reason is structural
rather than lucky.** `milestone_scope` skips every section at or below the anchor
(`subprojects/docket/src/docket/roadmap.py`, `if section.version <= anchor.version:
continue`). The anchor is now v0.5.0, so v0.4.0's `Required scope` places nothing at
all, and `bin/docket next product` no longer marks `PL-B9PY` (decompose
`SimulationView` so two runs can be rendered at once) as in scope for v0.4.0 — it
reports the Gate 1 placement, which is correct. Confirmed against `bin/docket wave`
and `bin/docket next product` on 2026-09-13. The anchor only moves forward, so this
particular bullet can never place anything again.

**The parser defect is still live, though, and it is worth one test.** Measured
against a synthetic section whose own `Required scope` names an id in order to
exclude it, with the id on no gate:

| id, and how the bullet names it | `Scope.placement` |
| --- | --- |
| genuinely in scope | `in-scope` — correct |
| named **only to be excluded** | `in-scope` — the defect |
| under `### Explicitly out of scope` | `unplaced` — `PL-6P9Y`'s finding, confirmed |

So the wrong direction is still reachable: an exclusion written inside the *anchor's
own* scope bullet, for an id the gate does not list, reads as in scope.

**The exposure is one bullet.** Counted across the whole of `ROADMAP.md`: 59 ids are
named under `Required scope` headings, and exactly **one** bullet carries exclusion
language — `ROADMAP.md:1160`, the `PL-B9PY` bullet this item was filed against. That
number is what chooses between the three candidates, and it was counted before the
choice rather than after.

**Why the second candidate, and why the other two lose on the count.**

- **The first** — read a bullet's ids only where it carries no exclusion marker — is
  the grammar guess `CLAUDE.md` says not to script, and it would be fitted to n=1.
  Worse, the guess would drive the placement itself, so a phrasing it misses prints a
  wrong marking silently. That is the failure mode this item exists to remove.
- **The third** — report an id named in both a scope bullet and an exclusion as
  `ambiguous` — has **zero** instances to work on: `PL-B9PY` is not named in
  v0.4.0's `### Explicitly out of scope for v0.4.0` list, so there is no contradiction
  for a decidable rule to find. Making it detectable means moving the exclusion into
  that list first, which is the second candidate. It is not an alternative to it; it
  is what the second candidate enables.
- **The second** moves the work out of the model permanently, which is `CLAUDE.md`'s
  standing approval rather than a case to be argued, and it needs no grammar guess for
  the part that fails hard.

**What gets built, in three parts and one of them marginal.**

1. **Move the exclusion.** `ROADMAP.md:1160`'s sentence sending `PL-B9PY` to Gate 1
   moves into `### Explicitly out of scope for v0.4.0`, keeping its reasoning and its
   attribution verbatim. One edit, and it is the whole of the live fix.
2. **An exact check, hard-failing.** An id named under a milestone's `Required scope`
   **and** under the same milestone's `Explicitly out of scope` is a contradiction:
   decidable, no judgment, an error. This is what stops part 1 being undone silently
   later, and it is the half that earns a hard failure under `CLAUDE.md`'s "reserve
   hard failure for exact rules".
3. **A keyword advisory, and it is the marginal part.** A `Required scope` bullet
   naming an id alongside `not in scope`, `out of scope` or `stays at Gate` is
   reported for a human to move. This *is* an imperfect grammar guess — but the
   failure direction inverts from the first candidate's: it changes no placement and
   only asks an author to rewrite a line, so a miss leaves the status quo and a false
   positive costs one rephrase. Named against the rule it enforces: worth building
   only if a future milestone writes another such bullet, base rate 1 in 59 ids across
   seven scoped milestones. Low, not zero, and the cost of a miss is a silent wrong
   marking in the command every session reads first.

A one-line writing convention in `ROADMAP.md` — exclusions go under the out-of-scope
heading, never inside a scope bullet — is what parts 2 and 3 cite. That sentence is
the project owner's to approve, being a convention for their own document.

**`PL-6P9Y`** (a milestone's `Explicitly out of scope` list is read as silence)
is the companion, and it is what makes part 1 produce the *right* answer rather than
merely not the wrong one: without it, moving the bullet turns `in-scope` into
`unplaced`; with it, into "excluded by v0.4.0", which is what the roadmap actually
says. It is `ready` at P3 and should land with this.

## Built 2026-09-13, and two corrections to the decision above

**The live fix.** `ROADMAP.md`'s v0.4.0 `Required scope` no longer discusses
stage 3 at all: the `PL-WB0X` bullet's head already said "stages 1 and 2 only",
so the excluding sentence was removed rather than reworded, and stage 3 is now a
bullet under `### Explicitly out of scope for v0.4.0` carrying the same
reasoning and the same attribution. `PL-B9PY` is out of v0.4.0's
`required_scope_ids` and in its `excluded_ids`, confirmed by parsing.

**The convention.** `ROADMAP.md` § "Development rules for scientific
milestones" now states the rule, beside the frozen-Goal rule it resembles, with
`PL-NBCS` cited for why it is written down rather than left to imitation.

**The parser.** `MilestoneSection` gains `required_scope_ids` (the scope
subsection alone, unmerged with the frozen list) and `excluded_ids`, with
`EXCLUDED_SUBSECTION` beside `SCOPE_SUBSECTION`. `scope_ids` is unchanged:
placement does not care which structure placed an id, and only the scope
subsection can contradict the exclusion heading.

**The checks, in `tools/doc_check.py`** - which already imports `docket.roadmap`
by path for exactly this reason, so the grammar has one home:

- **`check_scope_exclusions`, error half.** An id under both of one milestone's
  scope headings. Exact, no judgment, and it is what holds this fix in place
  against a later edit.
- **Advisory half.** A `Required scope` bullet carrying `not in scope`, `out of
  scope` or `stays at Gate` alongside an id. A keyword guess, admissible *here*
  and refused in the ranker for the reason the decision above gives: it changes
  no placement and only asks a person to move a sentence, so a miss leaves the
  status quo and a false positive costs one rewording.

**Correction one: the advisory is not the marginal half after all.** The
decision above called it the part that might not earn its place. Implementing
showed the opposite: the *error* half cannot catch the original shape, because
an exclusion written only inside a scope bullet produces no contradiction to
find. The advisory is the sole guard against the defect recurring, and the
convention sentence alone is prose a session may not read. It stays.

**Correction two: "excluded by v0.4.0" was wrong, and `PL-6P9Y` is not needed
here.** The decision above said moving the bullet would turn `in-scope` into
"excluded by v0.4.0" with `PL-6P9Y`, and `unplaced` without it. Both are beside
the point: `milestone_scope` reads no section at or below the anchor, the anchor
is v0.5.0, and `PL-B9PY` is placed `in-scope` by Gate 1's frozen list whatever
v0.4.0 says. So this item needed only the *parsing* half of `PL-6P9Y`, which is
now done - `PL-6P9Y` keeps the placement half and is smaller for it.

**One defect found in the check while writing it, worth recording because it
passed silently.** `_subsection_line` first returned a 0-based index where
`roadmap.py`'s convention is 1-based, so `_scope_bullets` began *on* the
`### Required scope` heading and stopped on it - zero bullets walked, advisory
never fired, `doc_check` reporting 0 advisories on a tree that had one. It was
caught only because the first ROADMAP.md rewording deliberately contained "out
of scope" and the advisory was expected to fire on it. A check watched failing
for the right reason is what separated that from a green run.

**Verified.** `verify:` exits 1 before the work and 0 after. `make check` green.
Docs swept: `ROADMAP.md` (edited), `docs/MODEL.md` (read, untouched by this
item), `subprojects/docket/README.md` (read, and **edited**: its
"What a milestone places" limitation said a milestone's `Explicitly out of
scope` list is "invisible", which is still true of the *ranking* and now
misleading about the *parse*, so the bullet names `excluded_ids`, the check
reading it, and `PL-6P9Y` as what would make it speak in placement).
