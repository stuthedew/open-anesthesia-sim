---
id: PL-KBVW
title: The generator pause binds while a head of either lane is live, so PL-X7D5, a run-view defect, froze apparatus housekeeping such as PL-ZYHX that the owner had approved: narrow the pause to workflow-lane heads, and add a measured cost paid on every run, session or commit as the fourth compounding-friction test (project owner, 2026-10-17, ratified)
priority: P2
effort: S
status: done
classes: docs, infra
feature: friction-batch
milestone: v0.5.25
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-10-17
closed: 2026-10-17
pr: 1484
payoff: a product-side generator head no longer freezes apparatus housekeeping the owner approved, and a measured cost paid on every run is a stated ground for offering work first, so the next PL-4Z5Y is offered rather than waited for
verify: grep -q 'paid on every run, session or commit' CLAUDE.md && grep -q 'workflow_paths' CLAUDE.md
---

**Problem.** The generator pause binds while a head of either lane is live, so PL-X7D5, a run-view defect, froze apparatus housekeeping such as PL-ZYHX that the owner had approved: narrow the pause to workflow-lane heads, and add a measured cost paid on every run, session or commit as the fourth compounding-friction test (project owner, 2026-10-17, ratified)

**Why it matters.** `CLAUDE.md` § "What this project is" pauses new workflow mechanisms and apparatus housekeeping while any open item carries `generator: live`. The rule was written on 2026-09-22 against six closed apparatus heads still producing (`PL-KVDK`). On 2026-10-17 the only live head was `PL-X7D5`, a run-view defect whose `touches` are all under `src/anesthesia_sim/app/`, and it held `PL-ZYHX`, apparatus housekeeping the owner had decided yes on 2026-10-03, and the two detection changes this batch asks for. A product-side head says nothing about whether the apparatus is generating. Ordinary evidence reopened the ratified decision, and the owner ratified the narrowing (project owner, 2026-10-17, ratified, over the pause binding while a head of either lane is live). The same reply asked whether the three compounding-friction tests reach a cost paid on every run: they do not, which is how `PL-4Z5Y` waited 20 days at about 15 minutes of CI a day, and the owner ratified a fourth test (over the three as they stood). `docs/WORKING_NOTES.md` § "Decided: the friction batch goes ahead of product work" carries the measurements.

**Done when.** The pause paragraph binds on an open item carrying `generator: live` whose `touches` lie in `workflow_paths` - the lane `Item.lane` already reads - and says so in one clause; the compounding-friction bullet lists a fourth test, "it is paid on every run, session or commit, at a measured cost"; both edits name what they replace, per the resident-set editing rule, and `docs/resident-instructions.md` records the test each stayed resident under. `make check` passes.

**Generator check.** Work the owner asked for, on a rule that forced the work rather than a fact a reader misread: the pause's "any open item" was written on 2026-09-22 when every live head was apparatus, so it never consulted the lane `Item.lane` already reads, and bound on `PL-X7D5`, a product head, as soon as one existed. No head's `misread:` states which heads a pause should bind on, and `PL-8ZGY`'s fact, which lane each tracked path is in, is read correctly by the lane reader this clause names. The fourth friction test is likewise a widening the owner ratified, not a misreading. Not a generator: one item, no sibling.
