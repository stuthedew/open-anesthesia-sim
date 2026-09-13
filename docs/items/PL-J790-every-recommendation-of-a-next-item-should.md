---
id: PL-J790
title: Every recommendation of a next item should state its relation to the current gate, and docket show never states one at all
priority: P2
effort: S
status: done
classes: defect
feature: dev-tooling
touches: .claude/skills/docket, subprojects/docket
added: 2026-09-13
closed: 2026-09-13
verify: uv run pytest -q subprojects/docket/tests/test_plan.py && grep -rq 'def test_an_unplaced_item_says_the_roadmap_places_it_nowhere' subprojects/docket/tests/
---

**Problem.** Every recommendation of a next item should state its relation to the current gate, and docket show never states one at all

**Why it matters.** A recommendation with no gate relation reads as *what the
project should do next*, whether or not it is. The project owner asked for the
relation to be stated, or for a deviation to be named as a deviation and
justified by urgency (2026-09-13).

The prompting failure: this session closed `PL-9SH6` and offered `PL-FZ6T` as
"the natural continuation", saying nothing about the gate. The skill already
had a rule for it - "Work the roadmap places nowhere ranks on its band alone
... Say so when you offer one" - but it sits under **Mode: recommend what to
work on**, and this was the closing block of a work session. The rule was right
and unreachable from where the offer was made.

**The tool half, which is the reason this is not prose alone.** `docket next`
prints the relation for two of the three placements. `Scope` has three -
`IN_SCOPE`, `OUT_OF_SCOPE`, `UNPLACED` - and `plan.py` writes a sentence for
the first two and nothing for the third, so an unplaced item's silence is
indistinguishable from a session not having looked. `bin/docket show` prints no
placement at all, which is worse, because naming an item is the path the owner
usually starts one on and the one `docket next` never sees.

**And the third relation is narrower than its name.** `Scope` reads exactly two
structures - a section's frozen list and its `Required scope` - so a milestone
recording scope in prose records it invisibly, and a timeline *row* places
nothing. `PL-FZ6T` is the worked example: `docket next` gives it no gate
sentence while `ROADMAP.md`'s `v0.4.x` row names it outright. Any sentence the
tool prints for `UNPLACED` has to say "no section places this", never "the
roadmap is silent", or it teaches every session to assert something false.

**Done when.** `docket next` states a relation for all three placements;
`bin/docket show` states one too; the `docket` skill's rule applies to any offer
of a next item rather than to one mode, and says what justifies recommending
off-gate work; `make check` passes.

**Where.** `.claude/skills/docket/SKILL.md`, `subprojects/docket/src/docket/plan.py`,
`subprojects/docket/src/docket/cli.py`, `subprojects/docket/tests/`.
