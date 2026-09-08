---
id: PL-36R4
title: "Thirty-eight presence-qualifying items carry neither a gate placement nor a recorded deferral, which is the one disposition ROADMAP's presence rule forbids"
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: planning-cadence
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-09-08
---

**Problem.** `ROADMAP.md` § "The gate is a snapshot, not a moving target"
requires a decision for every presence-qualifying finding and forbids exactly
one outcome: "a session may defer a presence-qualifying finding to the next
gate anyway, or decline to pull in one that only superficially resembles frozen
scope. **Either way it must say so and say why**: silently reinterpreting which
gate a finding belongs to is the renegotiation freezing the list exists to
prevent."

Measured 2026-09-08 against the frozen Gate 1 list and v0.5.0's `Required
scope`: **38 open items** classed `defect`/`refactor`/`perf` or at
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

**Done when.** Every one of the 38 either appears in the frozen list under a
dated group heading, or carries a recorded reason for deferring to Gate 2; and
a check exists that reports the same class of silence without deciding it, at a
place and cadence where its output changes a decision rather than accumulating.
