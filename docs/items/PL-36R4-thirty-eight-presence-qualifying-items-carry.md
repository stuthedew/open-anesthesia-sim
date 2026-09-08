---
id: PL-36R4
title: "Forty-two presence-qualifying items carry neither a gate placement nor a recorded deferral, which is the one disposition ROADMAP's presence rule forbids"
priority: P2
effort: M
status: done
classes: defect, infra
feature: planning-cadence
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-09-08
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_an_open_debt_item_the_gate_neither_places_nor_defers_is_reported' tests/unit/test_doc_check.py
closed: 2026-09-08
---

**Problem.** `ROADMAP.md` § "The gate is a snapshot, not a moving target"
requires a decision for every presence-qualifying finding and forbids exactly
one outcome: "a session may defer a presence-qualifying finding to the next
gate anyway, or decline to pull in one that only superficially resembles frozen
scope. **Either way it must say so and say why**: silently reinterpreting which
gate a finding belongs to is the renegotiation freezing the list exists to
prevent."

Measured 2026-09-08 against the frozen Gate 1 list and v0.5.0's `Required
scope`: **42 open items** (38 when first measured on 2026-09-08; four have arrived since) classed `defect`/`refactor`/`perf` or at
`needs-decision` are placed in neither, and none carries a recorded deferral.
Every one is dated 2026-09-06 or 2026-09-07 — on or after the freeze — so each
is presence-qualifying or arguably so, and each therefore owes the decision the
passage above demands. Twenty-three are dated 2026-09-06, fifteen 2026-09-07.
By feature: 12 `dev-tooling`, 8 `parallel-sessions`, 5 `release-process`, 4
`presentation-safety`, and one each in five others.

**This is not the same defect as `PL-KTKP`, and the difference is the point.**
That item found eleven `safety`/`science` entries missing and built
`check_gate_reentries` in `tools/doc_check.py` to stop it recurring. That check
is correctly scoped and should not be widened as it stands: its own docstring
says the `safety`/`science`/`P0` rule "is decidable, this one is not", because
every other class "defers to the next gate unless its problem predates the
freeze, which is a judgment call". So the check deliberately does not decide
these — and nothing else asks anyone to. The judgment the rule requires is
never prompted, so it is never made, and the result is the silence the rule
names as the forbidden outcome.

**Why it matters.** `bin/docket wave` reads the written list to report the beat,
so the gate can read clear while several dozen items its own rule may place
inside it have had no disposition recorded either way. That is the
silent-wrong-answer shape `CLAUDE.md`'s compounding-friction test names, and it
is the shape `PL-KTKP` already found once in the other half of the same rule.
The cost is also concentrated rather than spread: 4 of the 38 are
`presentation-safety`, the lane whose entries `PL-YKF8` records can only be
confirmed by eye.

**Where.** `tools/doc_check.py` — beside `check_gate_reentries`, which is the
model for what this should look like and the reason it must not simply be
widened.

**Decision needed.** It is a design question rather than a coding one. What
is decidable is placement (`MilestoneSection.scope_ids` already answers it) and
whether a deferral has been *recorded*. What must not be scripted is which way
each of the 38 goes — a problem introduced by gate-clearing work on 2026-09-06
or 09-07 legitimately defers, and two or three (`PL-YKXQ`, `PL-483K`) look like
they may. So the shape is an advisory naming candidates, not an error and not
an auto-placement.

The open question is where it fires. A `make check` advisory listing 38 items
every run is precisely the check `CLAUDE.md` calls a defect — one that "fires
every run without changing a decision", costing attention forever and training
a session to skim the output where a real advisory also appears. A
`bin/docket` subcommand run at gate time, or an advisory that names only items
`docket next` is about to offer (the narrowing `PL-MHQK` argues for), are the
two candidates. Deciding that is the item.

## The audit, run 2026-09-08

Every open item classed `defect`/`refactor`/`perf` or at `needs-decision`,
absent from both the frozen list and v0.5.0's `Required scope`. Forty-two, by
feature:

- **dev-tooling** (12): PL-0M32, PL-2GQW, PL-483K, PL-6G8T, PL-7RTN, PL-F48B,
  PL-JW39, PL-K5PW, PL-KNHX, PL-LT77, PL-T7VS, PL-YKXQ
- **parallel-sessions** (8): PL-12P8, PL-6BDX, PL-8MJ3, PL-G8TR, PL-JBRC,
  PL-P757, PL-Y1LD, PL-Y31G
- **presentation-safety** (5): PL-0Q1T, PL-2CS8, PL-CZFY, PL-NGF7, PL-THXF
- **release-process** (5): PL-6YYR, PL-KFWL, PL-KRS6, PL-PNW6, PL-VYK1
- **planning-cadence** (3): PL-36R4, PL-TNB6, PL-WSDY
- **one each**: PL-3PRZ (core-guard-coverage), PL-8GV5 (model-spec-accuracy),
  PL-8P6D (public-readiness), PL-B9VL (numerical-domain), PL-F9TQ
  (teachable-case), PL-L7JB (core-domain-language), PL-LPWK
  (commit-provenance), PL-QV5Y (ci-cost), PL-XF89 (project-introduction)

**Applying the presence test item by item gives an almost unanimous answer,
and that is the finding.** The rule defers only "when the problem itself is
new: introduced by work done while clearing this gate or implementing the
milestone it protects". Read against each brief, that exempts **one**:

- **PL-2GQW** — `PL-L9JS`'s `not-delegable` reason rests on a recursion claim
  `PL-20CQ` disproved, and `PL-20CQ` closed 2026-09-07, after the freeze. The
  staleness did not exist until that item landed. Defers to Gate 2.

Four more look like exceptions and are not, because the rule tests the
*problem* rather than the observation. Each names a mechanism that predates
the freeze and an instance that does not:

- **PL-6YYR**, **PL-KFWL**, **PL-PNW6** — all three are the v0.4.8 tag pushed
  on 2026-09-07 for a version never cut. The instance is post-freeze; what
  each item actually describes is that *nothing detects it*, which was true on
  2026-09-06. Note separately that the incident appears resolved on the
  current tree: `v0.4.8` was subsequently cut and `doc_check` is clean, so
  **PL-KFWL** in particular may be closeable rather than placeable, and that
  should be checked before it is put anywhere.
- **PL-YKXQ** — a clone left on pre-rewrite history. Same family as
  **PL-F48B** (nothing repairs a clone's tags after a rewrite), which nobody
  would call new. Present.

So the mechanical answer is **41 into Gate 1, 1 deferred**, taking the gate
from 132 entries to 173.

**Decision needed.** Which is why this is not a mechanical answer at all, and
the volume is the argument rather than an objection to it. `ROADMAP.md` §
"Presence is a presumption, not an absolute rule" gives exactly one other
ground for declining, and it fits: "pulling it in would recreate the
refilling-queue problem the debt gate replaced Phase 0 to solve". Gate 1 is
already by a wide margin the largest this project has held — 132 against Gate
0's 21 — and 41 more would grow it by 31% at a point where 89 of the existing
entries are still open. That is the shape Phase 0 was retired for: a gate that
refills faster than it drains is one that gets abandoned rather than followed,
which is worse than not having it.

Three routes, and the project owner picks:

1. **Admit all 41.** Faithful to the presumption, and the gate becomes 173.
2. **Admit the safety-relevant subset and decline the rest with the
   refilling-queue reason recorded.** The five `presentation-safety` entries
   are the ones with a reader-facing consequence; the twenty `dev-tooling` and
   `parallel-sessions` entries are apparatus, held to a deliberately lower bar
   by `.claude/rules/apparatus-standard.md`, and are the bulk of the volume.
3. **Decline the lot to Gate 2, with the reason recorded**, and treat the
   whole post-freeze cohort as the next gate's.

Route 2 is the recommendation. It is the only one that neither inflates the
gate past what it can drain nor lets a reader-facing defect wait, and the
apparatus/simulator split it keys on is one the project already draws for
exactly this kind of triage.

**Whichever is chosen, the check is the same and is the durable half.** The
decision above is one afternoon; the mechanism that stops the silence
recurring is what this item is for.

**Outcome (project owner, 2026-09-08): route 2, on `docket.toml`'s own lane
boundary.** The recommendation named "the five `presentation-safety` entries"
against "the twenty `dev-tooling` and `parallel-sessions` entries", which
accounted for only 25 of the 42 and was a sketch rather than a rule. Applying
the project's existing `workflow_paths` boundary to each item's `touches`
instead makes the split decidable and complete: **13 admitted** - the ten in
the product lane and the three reaching both halves - and **29 declined**, all
of them wholly in the workflow lane. Gate 1 goes to 145 entries rather than the
173 the mechanical answer would have given. Both groups are written into
`ROADMAP.md` under dated headings, the declined one carrying the
refilling-queue reason the rule requires.

`check_gate_dispositions` in `tools/doc_check.py` is the durable half. It is an
advisory, it decides nothing, and it is quiet today because every open debt
item now carries a disposition - which is what stops it becoming the check
`CLAUDE.md` calls a defect. Six tests cover it, including one against the real
tree; `PL-PDP6` records that its sibling `check_gate_reentries` has none.

**Done when.** Every one of the 38 either appears in the frozen list under a
dated group heading, or carries a recorded reason for deferring to Gate 2; and
a check exists that reports the same class of silence without deciding it, at a
place and cadence where its output changes a decision rather than accumulating.
