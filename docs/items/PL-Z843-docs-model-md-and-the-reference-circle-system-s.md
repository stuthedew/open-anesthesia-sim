---
id: PL-Z843
title: docs/MODEL.md and the reference circle system's data file say no surveyed machine publishes a startup fresh gas flow, though the survey read no manufacturer's manual
status: untriaged
feature: machine-docs-structure
added: 2026-11-11
touches: docs/MODEL.md, src/anesthesia_sim/data/machines/reference_circle_system.json
---

**Problem.** Two files give a stronger reason for the 4.0 L/min fallback flow than the survey supports.

- `docs/MODEL.md` § "Where each stored value comes from": "**The default is also the flow a run starts at when a machine profile states none**, because no surveyed machine publishes a startup flow."
- The `provenance_gap` of `src/anesthesia_sim/data/machines/reference_circle_system.json`: "No surveyed machine publishes a startup fresh gas flow; docs/machine-survey.md section (a2) records the search and what it returned."

The survey's search reached no manufacturer's manual (`docs/machine-survey.md` § "How a value gets into this document"). On 2026-11-11 `PL-8ZD7` narrowed the survey's own wording to "no source found gives one". A contributor who writes a machine profile from either copy is told that the manual holds no startup flow to look for. The profile may then state none, and a run for that machine opens at 4.0 L/min instead of the machine's own startup flow.

**Fix.** In both places, say that no source the survey reached gives a startup flow for any machine, and keep the rest of each sentence.

**Done when.** Neither file says that no surveyed machine publishes a startup flow.

**Found by** both blind review passes on #2112 (2026-11-11). A defect in `docs/MODEL.md` or a data file is filed rather than fixed in place, so it is not fixed on that branch.
