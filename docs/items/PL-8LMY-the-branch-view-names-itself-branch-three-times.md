---
id: PL-8LMY
title: The Branch View names itself 'Branch' three times: in its Area header, as its panel heading, and on its button
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
milestone: v0.6.19
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/approved_interface_strings.json
added: 2026-11-22
closed: 2026-11-22
pr: 2206
payoff: the Branch Area gives a row back and names itself once
tests: tests/integration/test_agent_cost_view.py::test_the_branch_view_has_no_heading_of_its_own
---

**Problem.** The Branch View names itself 'Branch' three times: in its Area header, as its panel heading, and on its button

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** The Branch Area's header says "Branch", the panel's
first line says "Branch" in bold, and the button says "Branch"
(`ws0-Default-1366x768.png`). Every other View's Area header names it once,
and the Parameters View has no panel heading at all.

**Why it matters.** Since every View sits in an Area, the header already names
it. The repeated heading costs a row in a short Area and adds no information.

**What to do.** Remove the panel heading from the Branch View. The header
keeps the name, and the button keeps its label, because that names the act.

**Done when.** The Branch View shows no heading of its own, and a test checks
that "Branch" appears once as a label in the View.

**Reproduced 2026-11-22** on `a7eb53f`, offscreen: `ws0-Default-1366x768.png`.

**Generator check.** A one-off: the heading dates from when the branch control was a fixed page section under the Areas, before `PL-9YPR` made it a View whose Area header names it.

**Built 2026-11-22.** `ForkPanel` loses `heading_label`.

**Regression run.** The new test, run against the code before the fix, failed with `assert 'Branch' not in ['', 'Branch', 'From', '']`.

**Docs swept 2026-11-22.** `docs/INTERFACE.md`, `docs/ARCHITECTURE.md` and `README.md`, searched for the changed wording and for the element's look; none states it, so none changed.
