---
id: PL-W04Z
title: Make close-out step 8's prose review run on every simulator branch that changes long prose: only 1 of the 6 simulator branches that held the step from 2026-10-18 to 2026-10-19 recorded running it (#1619), and the 5 that did not wrote prose rated 58% awkward against 22% for #1619 (PL-J6CK)
status: untriaged
feature: prose-quality
added: 2026-10-19
---

**Problem.** Close-out step 8 in `.claude/skills/docket/modes/close-out.md`
has a fresh reviewer rewrite each long docstring and comment that a branch adds
to the simulator. `PL-J6CK` measured it on 2026-10-19 and kept it. Six
simulator branches were cut after the step merged (#1598) and merged before
that measurement: #1606, #1609, #1612, #1617, #1618 and #1619. Only #1619 says
in its pull request body that the review ran, as step 8 asks. The prose of the
other five was rated awkward in 35 of 60 blind verdicts (58%), against 13 of 60
(22%) for #1619. So the step works when it runs, but most sessions skip it.

**What to find out.** Why the five sessions skipped the step. Step 8 sits after
steps 5 to 7 in the file but runs before step 5's audit, and nothing checks
that it ran. A check could refuse a simulator pull request whose body lacks the
counts line that step 8 asks for, whenever `tools/new_prose.py` prints a unit.
Whether that check is worth its cost, or a plainer place for the step is
enough, is the question for this item.

`/mnt/project-files/v0.6.0/plain-writing/remeasure-2026-10-19/` holds the
ratings and the scripts.
