---
id: PL-RCTQ
title: Sweep MODEL.md and README for the new unit, time base and run rate
priority: P2
effort: S
status: ready
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
