---
id: PL-JV5H
title: The Reset, new-case and Workspace questions are windows that cover required readouts while open, with every run waiting, and docs/INTERFACE.md's occlusion rule has no sentence that allows it (found while building PL-CHX0)
priority: P2
effort: S
status: needs-decision
classes: defect
feature: interface-matches-its-spec
touches: docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: the interface specification says when a question may cover a required readout, so the code and the rule no longer read as in conflict
---

**Problem.** The Reset, new-case and Workspace questions are windows that cover required readouts while open, with every run waiting, and docs/INTERFACE.md's occlusion rule has no sentence that allows it (found while building PL-CHX0)

**Found 2026-11-22 while building `PL-CHX0`**, and named in that item's brief. `docs/INTERFACE.md` § "What this list requires once the layout is the reader's" says that no value the list requires may be covered while the application treats it as shown, and that the rule applies to the application's own windows. The questions that block the window (Reset, a new case, a Workspace change) are such windows and sit over the dashboard while open. Every run waits while one is open (`PL-TPBH`), so nothing under it changes, but the document has no sentence saying why a covered value is allowed then. Qt cannot place a top-level window under Wayland (Qt 6.12, "Window and Dialog Widgets", § "Wayland Peculiarities", cited in `PL-CHX0`), so a placement rule cannot close this either.

**Why it matters.** `docs/INTERFACE.md` says no required value may be covered while the application treats it as shown. The three questions cover required readouts, and the document does not say why that is allowed, so a later contributor reads the code and the rule as in conflict.

**Decision needed.** Should `docs/INTERFACE.md` add an exception for a question that blocks the window while every run waits, or should the three questions move into the window so that they cover nothing?

**Recommendation (provisional).** Add the exception, stated with its condition (every run waits, so nothing under the question changes), because Qt cannot place a top-level window under Wayland and moving three questions inline is larger work. It changes a safety rule's wording, so it goes to the owner after the research on modal dialogs over monitored values is recorded here. [superseded 2026-11-27: the research below reverses it.]

**Research, 2026-11-27.** Four sources bear on it, each read in full on that date.

1. **The closest analog, a patient monitor, never lets a window cover its identity and alarm lines.** Philips IntelliVue MX400 to MX800 Instructions for Use, Release K and J, part number 453564443141, published 11/2013, section "Moving Windows", page 30 (PDF read from https://medaval.ie/docs/manuals/Intellivue-Manual.pdf): "Not all locations on the screen can be a target position, a window cannot overlap the monitor info line, the alarms and INOPs or the status line." The info line holds the patient's name, the date and time and the current screen. Its windows may cover waveforms and numerics in the main screen area. The monitor keeps measuring while a window is open.
2. **NUREG-0700 Rev. 3** (O'Hara JM, Brookhaven National Laboratory for the US Nuclear Regulatory Commission, July 2020, read from https://www.osti.gov/servlets/purl/1644018): 2.5.2-22, "It should not be possible to position a window so that it obscures menu bars, access to the command area, or caution and warning messages." 2.5.2-38, "A temporary window object should not obscure critical control information and command entry interfaces of the active window." 2.5.2-37 allows display data to be "temporarily obscured by a window object" if it "should reappear when the object is removed." 2.7.5-1 asks for confirmation before a destructive entry, which is what these questions are.
3. **This document's own rule for the questions**, `docs/INTERFACE.md` § "Discarding a run, and the questions that guard it": "The question must name what will be lost in the terms that the display already uses, so that the user can check it against the readouts." A window over the readouts stops the user doing that check.
4. **The owner's decision for the marks editor**, `docs/INTERFACE.md` § "No required value may be covered" (project owner, 2026-11-21, ratified): the marks are edited in a View, "over a window kept off the readouts, an exemption from this rule, and an editor during which every run waits", because the application cannot keep a window off the readouts under Wayland (Qt 6.12, "Window and Dialog Widgets", § "Wayland Peculiarities", cited in `PL-CHX0`).

So the exception would let a window cover the run's time, agent and banner, which the closest analog forbids and NUREG-0700 forbids for the warning banner. Every run waits while a question is open, so 2.5.2-37's condition holds, and nothing a user could misread changes underneath. The cost of the exception is the check the question itself asks the user to make.

**Decision needed (restated 2026-11-27).** While a Reset, new-case or Workspace question is open, may it cover the readouts, the run's banner and the charts?

1. **Show each question inside the window, between the readout band and the Workspace tabs, so that it covers nothing.** The user sees every readout while deciding. The tabs and Areas below move down while it is open, and they come back when it closes. Every run still waits. This is a build of medium size: the three questions are rebuilt as one in-window question, with a dialog's keyboard behaviour (Return keeps, Escape keeps, focus starts on Keep) and its screen-reader announcement. Input outside the question is blocked without drawing any agent control as disabled (`.claude/rules/ui-color.md`). The tests that open these questions move to it.
2. **Allow the question window to cover them while every run waits.** `docs/INTERFACE.md` gains one exception, conditioned on the wait, and the existing tests that every run waits while each question is open are the test (`test_the_run_does_not_advance_while_a_reset_question_is_open` in `tests/integration/simulation_view/test_simulation_view_comparison.py`, and the two beside it). The user may not see the readouts that the question asks them to check.

**Recommendation: option 1.** It meets the occlusion rule with no exception, keeps the run's time, agent and banner in view as the IntelliVue rule does for its info line and alarms, and lets the user check the question against the readouts as this document requires. It also matches the owner's choice for the marks editor. Option 2 is a one-sentence change, but it would be the first exemption to a display safety rule. This is the owner's call, because it decides whether a value the safety standard requires is on screen (`.claude/rules/instruction-writing.md` rule 14, `PL-KBBJ`).

**Done when.** The decision is recorded here, and either `docs/INTERFACE.md` carries the exception with a test that every run waits while each question is open, or the questions no longer cover a required value.

**Generator check.** A one-off, found while building `PL-CHX0`.
