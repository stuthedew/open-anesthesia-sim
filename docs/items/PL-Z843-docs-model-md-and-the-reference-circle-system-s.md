---
id: PL-Z843
title: docs/MODEL.md and the reference circle system's data file say no surveyed machine publishes a startup fresh gas flow, though the survey read no manufacturer's manual
priority: P3
effort: S
status: ready
classes: defect
feature: machine-docs-structure
touches: docs/MODEL.md, src/anesthesia_sim/data/machines/reference_circle_system.json
deferred-from: v0.7.0 - present at the freeze, with no real connection to v0.7.0's Required scope: it matters when a second machine profile is written, which the deferred PL-WZVZ and PL-B4P7 wait on and no release schedules
added: 2026-11-11
payoff: A contributor writing a machine profile is told to look for the machine's own startup flow rather than assuming none is published.
reenters: PL-4FBP
---

**Problem.** Two files give a stronger reason for the 4.0 L/min fallback flow than the survey supports.

- `docs/MODEL.md` § "Where each stored value comes from": "**The default is also the flow a run starts at when a machine profile states none**, because no surveyed machine publishes a startup flow."
- The `provenance_gap` of `src/anesthesia_sim/data/machines/reference_circle_system.json`: "No surveyed machine publishes a startup fresh gas flow; docs/machine-survey.md section (a2) records the search and what it returned."

The survey's search reached no manufacturer's manual (`docs/machine-survey.md` § "How a value gets into this document"). On 2026-11-11 `PL-8ZD7` narrowed the survey's own wording to "no source found gives one". A contributor who writes a machine profile from either copy is told that the manual holds no startup flow to look for. The profile may then state none, and a run for that machine opens at 4.0 L/min instead of the machine's own startup flow.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "publishes a startup" docs/MODEL.md src/anesthesia_sim/data/machines/reference_circle_system.json` still finds "because no surveyed machine publishes a startup flow" in `docs/MODEL.md` and "No surveyed machine publishes a startup fresh gas flow" in the data file's `provenance_gap`. `docs/machine-survey.md` now says "No reachable source states a startup fresh gas flow". The claim is about how far the evidence goes, and no stored or displayed value changes with it: the one shipped machine profile states its own default flow of 4.0 L/min.

**Why it matters.** A contributor who writes a profile for a real machine is told that its manual holds no startup flow, so they may not look for one. The run for that machine would then open at the 4.0 L/min fallback instead of the machine's own startup flow.

**Fix.** In both places, say that no source the survey reached gives a startup flow for any machine, and keep the rest of each sentence.

**Done when.** Neither file says that no surveyed machine publishes a startup flow.

**Found by** both blind review passes on #2112 (2026-11-11). A defect in `docs/MODEL.md` or a data file is filed rather than fixed in place, so it is not fixed on that branch.

**Generator check.** An instance of the fact that `PL-4FBP` (a document sentence's link to the tree lives only in the reader's head) names, filed after that head closed on 2026-09-19: the link between a document sentence and the tree fact it restates. Both sentences restate the survey's finding, and `PL-8ZD7` narrowed the finding in `docs/machine-survey.md` without either copy changing.
