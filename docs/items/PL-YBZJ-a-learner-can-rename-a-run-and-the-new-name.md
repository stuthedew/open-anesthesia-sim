---
id: PL-YBZJ
title: A learner can rename a run, and the new name shows on the run's panel, its readouts and both chart legends, while a Workspace's pin stays on the run's identity (PL-7Z84) rather than its name (project owner, 2026-10-19: 'Will eventually want users to be able to rename run names if they want')
status: untriaged
added: 2026-10-19
---

**Problem.** A learner can rename a run, and the new name shows on the run's panel, its readouts and both chart legends, while a Workspace's pin stays on the run's identity (PL-7Z84) rather than its name (project owner, 2026-10-19: 'Will eventually want users to be able to rename run names if they want')

**Where it fits.** `dashboard_frame.run_label` is the one place a run is
named, so the panel heading, the readouts and both legends already agree.
A rename would hold the learner's name beside the run's `RunId` and have
`run_label` render it. The pin is by `RunId`, so a rename cannot move a
Workspace onto another run. One point needs care under the safety-critical
standard: two runs must never show the same name, or a legend entry no
longer tells the reader which run's settings produced a curve. So a rename
to a name another open run holds is refused, with the reason on screen.
"Eventually" in the owner's words, so this waits for its milestone.
