---
id: PL-47SP
title: Cut v0.5.14 from the 17 items finished since v0.5.13
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-27
payoff: the 17 items finished since v0.5.13 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.14\"" pyproject.toml
---

**Problem.** Cut v0.5.14 from the 17 items finished since v0.5.13

The project owner asked for it on 2026-09-27 ("cut new version"), with the
session-start digest offering 0.5.14 on 17 finished items completing
`bash-guard-bound` and `interface-pass-narrative`.

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.13 as
the annotated tag `6abf31b4` peeling to `c7fcd6f2`, the cut's own merge
(`#1141`), so the cut is not refused on an untagged predecessor. `bin/docket
flight` shows no release item claimed - its one row is `PL-384P` on
`claude/nifty-hawking-gvi5r7` - and `list_sessions` shows no other session
cutting one: the three running beside this one are a triage pass, `PL-384P`,
and `PL-FBY3`'s session confirming its own merge. `bin/docket release
--dry-run` named 17 finished items, and they match `main`'s own history: the 19
pull requests merged after `#1141`, whose ids not among the 17 are `PL-P813`,
`PL-Y04W`, `PL-MLRX` and `PL-N6JP`, all `dropped`, and `PL-5XG1`, `blocked` -
and an item not `done` ships in no release.

**The version is a patch**, on both halves of `ROADMAP.md` § "Versioning
decision": nothing a learner can reach moved, measured by tree object -
`src/anesthesia_sim/core/` resolves to `d9e3ca9f`, `src/anesthesia_sim/data/`
to `ab3499fd`, `src/anesthesia_sim/app/` to `f3c6e26e` and `tests/reference/`
to `a1848300` at both ends - and every minor from v0.6.0 up is given to a
milestone. What did move is `docs/MODEL.md`, +210 lines of prose from
`PL-WMCJ` and `PL-FBY3`: intertissue diffusion is now a named assumption and
known limitation, with the direction it biases the fat compartment, which is a
statement about the model rather than a change to it.
