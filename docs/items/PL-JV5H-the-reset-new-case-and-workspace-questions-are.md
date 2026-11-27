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

**Recommendation (provisional).** Add the exception, stated with its condition (every run waits, so nothing under the question changes), because Qt cannot place a top-level window under Wayland and moving three questions inline is larger work. It changes a safety rule's wording, so it goes to the owner after the research on modal dialogs over monitored values is recorded here.

**Done when.** The decision is recorded here, and either `docs/INTERFACE.md` carries the exception with a test that every run waits while each question is open, or the questions no longer cover a required value.

**Generator check.** A one-off, found while building `PL-CHX0`.
