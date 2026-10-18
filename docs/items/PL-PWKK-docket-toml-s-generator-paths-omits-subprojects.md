---
id: PL-PWKK
title: docket.toml's generator_paths omits subprojects/docket/src/docket/inflow.py, though its re-entered list is where triage's three-post-close rule finds a generator whose fix did not hold, so a defect confined to inflow.py cannot carry impairs-generators (found triaging PL-C4F0, 2026-10-17)
priority: P2
effort: S
status: done
classes: infra, defect
milestone: v0.5.28
touches: docket.toml
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-18
pr: 1536
payoff: a defect in the re-entry count that finds a generator whose fix did not hold can be ranked with the generators instead of waiting on its band
verify: grep -qF '"subprojects/docket/src/docket/inflow.py"' docket.toml
---

**Problem.** docket.toml's generator_paths omits subprojects/docket/src/docket/inflow.py, though its re-entered list is where triage's three-post-close rule finds a generator whose fix did not hold, so a defect confined to inflow.py cannot carry impairs-generators (found triaging PL-C4F0, 2026-10-17)

**Checked 2026-10-17.** `grep inflow docket.toml` finds nothing.
`generator_paths` lists `plan.py`, `model.py`, `checks.py`, `render.py`,
`cli.py`, `config.py` and `tools/generator_check.py` with its test.

**Why it matters.** `bin/docket check` refuses an `impairs-generators:` claim on
an item whose `touches` miss `generator_paths`. So a defect in `inflow.py`'s
re-entry count, which is how triage finds a generator whose fix did not hold,
cannot be ranked with the generators, and would wait on its band.

**Done when.** `generator_paths` in `docket.toml` names
`subprojects/docket/src/docket/inflow.py`.

**Generator check.** One-off. The fact is "which modules are generator
machinery", and `generator_paths` is its record. `inflow.py` was added by
`PL-WXKD` without updating it. No other module is known to be missing.
