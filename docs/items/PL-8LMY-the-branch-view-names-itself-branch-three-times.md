---
id: PL-8LMY
title: The Branch View names itself 'Branch' three times: in its Area header, as its panel heading, and on its button
status: untriaged
feature: interface-design-review
added: 2026-11-22
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
