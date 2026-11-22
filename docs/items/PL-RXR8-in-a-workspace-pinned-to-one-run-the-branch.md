---
id: PL-RXR8
title: In a Workspace pinned to one run, the Branch View offers Branch here with nothing saying the comparison will not be drawn there, so a learner finds out only after the one comparison slot is filled
status: untriaged
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-11-22
---

**Problem.** `PL-YQ5J` made the Branch View say, after the press, that a
pinned Workspace does not draw the comparison and how to unpin it. Before the
press, the same Workspace offers "Branch here" and the run selector with no
hint that the result will not be drawn there. A branch cannot be undone short
of starting the case over: the branch's Reset returns it only to its fork
point, and the trunk's Reset restarts the case. So a learner in a pinned
Workspace learns where the branch went only after it has filled the one
comparison slot.

**Where it came from.** Pass 1 of the blind review of pull request #2239, on
2026-11-22, marked it optional. It is a design addition beyond `PL-YQ5J`'s
fix, so it is filed rather than built there.

**What to do.** Show a short conditional line beside "Branch here" while the
Workspace is pinned, saying the comparison will open in an unpinned Workspace.
Read the pin the same way `SimulationView._compared_runs` does, so the two
sentences cannot disagree. `.claude/rules/expert-review.md` prefers an
interface that prevents an error to one that reports it.

**Generator check.** One instance. The cause is that `PL-YQ5J` fixed the
report after the press and not the offer before it.

**Done when.** A test pins a Workspace, opens its Branch View before any
branch, and finds the line; and finds it gone once the Workspace is unpinned.
