---
id: PL-RCTQ
title: Sweep MODEL.md and README for the new unit, time base and run rate
priority: P2
effort: S
status: blocked
blocked-by: PL-VM40, PL-SN2C, PL-SSBP, PL-CC23, PL-DR1Z, PL-ZRSP, PL-R3KB, PL-W3DD
classes: docs
feature: teachable-case
touches: docs/MODEL.md, README.md
added: 2026-08-25
---
**Problem.** The v0.3.0 milestone changes what the interface asserts: a second
displayed unit, a case-length time base, a run-rate control, a recorded input
timeline, and a reference band. `docs/MODEL.md`'s "Interface boundary", "Minimum
displayed outputs" and "Displayed precision" sections and `README.md`'s status
section all describe the interface as it was before that.

**Why it matters.** Stale documentation is a safety issue in this repository rather
than untidiness: a reader who trusts a wrong statement about what a displayed value
means can reach a wrong conclusion from a correct number. `README.md` currently
states that MAC is used only to pick a starting dial position and that no
MAC-fraction readout is displayed, which the milestone makes false.

**Where.** `docs/MODEL.md` § "Conventions", § "Runtime controls", § "Interface
boundary", § "Minimum displayed outputs", § "Displayed precision"; `README.md`
§ "Current status".

**Done when.** Both documents describe the interface the milestone actually ships;
the minimum-displayed-outputs list includes the run rate and the active unit; the
interface boundary states the fixed-step and no-catch-up guarantees from PL-VM40;
`make doc-check` passes; and `python3 tools/doc_check.py candidates --base <ref>`
has been run over the milestone's diff and each surfaced line judged for truth
rather than only for path validity.

**What v0.4.1 does to this (added 2026-09-03).** Four of this sweep's
`docs/MODEL.md` targets are rewritten one release later, so anything written here
that ties a displayed unit's precision to the numerical method is false at
v0.4.1: § "Displayed precision" and § "Supported simulation step" by `PL-X9KD`,
§ "Selected method (as implemented)" by `PL-GS5X`, and §§ "Symbols" and
"Conventions" by `PL-3TLK`, `PL-H46J` and `PL-212V`.

Write the sweep so it survives: state the new unit, time base and run rate in
their own terms, and cite § "Displayed precision" for the resolution rather than
restating the derivation. A restated derivation is a second thing to keep true,
and this one is about to change.

**Blocked on the milestone it sweeps (2026-09-04, project owner, deciding
`PL-5WFS`).** Sequencing only. A documentation sweep of v0.4.0 cannot be
written before v0.4.0, and this item's own "Done when" says so twice: it
requires "the fixed-step and no-catch-up guarantees from PL-VM40", and that
`python3 tools/doc_check.py candidates --base <ref>` "has been run over the
milestone's diff" — a diff that does not exist until the milestone does.
Before this edit `bin/docket next` offered it 6th of 9, startable today.

**Which ids, and the rule for maintaining the list.** The blockers are the
open `teachable-case` items that change something this sweep must describe,
drawn from this brief's own "Problem" and "Where" rather than from a judgment
about the milestone: `PL-VM40` (the fixed-step guarantees), `PL-SN2C` (the run
rate), `PL-SSBP` (the case-length time base), `PL-CC23` (the vertical scale),
`PL-DR1Z` (the recorded input timeline), `PL-ZRSP` (the F_A/F_I trace and its
constant-F_I caveat), `PL-R3KB` (the agent-change confirmation) and `PL-W3DD`
(the history record's shape, § "Interface boundary"). `PL-011` is deliberately
absent: a memory bound is not an assertion either document makes.

An item added to this milestone that changes what `docs/MODEL.md` or
`README.md` assert belongs in this list. `docket check` raises "every blocker
has closed; it is ready to promote" when the last one lands, which is exactly
when this sweep becomes writable.

**The README half is frozen.** `PL-QTN6` (freeze README edits) holds
`README.md` until the project owner answers `PL-RM83` (decide what README.md
is for). Sweep `docs/MODEL.md` when this unblocks, record the README lines
that went stale as a finding, and leave the file alone; see
`.claude/rules/readme-hold.md`.

**One line outside `docs/MODEL.md` that this sweep should also settle
(2026-09-05, landing `PL-SSBP`).** `ROADMAP.md`'s v0.4.0 "Goal" gives three
measurable reasons the model is unteachable, and its second reads "the chart
shows a rolling five-minute window on an axis labelled in seconds and scaled
to the vaporizer's dial maximum". All three clauses are now false: `PL-CC23`
fixed the vertical scale and `PL-SSBP` the window and the axis units. The
section is a snapshot of the state at scoping rather than a description of
what ships - `PL-CC23` landed without amending it, which is the convention -
so it was left alone rather than edited unilaterally. Decide as part of this
sweep whether a scoping-time Goal should say so in its own words, and apply
the same answer to all three clauses at once.
