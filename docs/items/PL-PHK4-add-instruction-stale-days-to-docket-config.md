---
id: PL-PHK4
title: Add instruction_stale_days to docket config, defaulting to 90, with synthetic-date tests so the advisory is tested before it first fires
priority: P2
effort: S
status: done
classes: infra
feature: instruction-staleness-audit
milestone: v0.5.3
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/README.md, subprojects/docket/tests, docket.toml
added: 2026-09-21
closed: 2026-09-21
pr: 883
payoff: the advisory is proven working 69 days before it first fires, not discovered broken when it does
verify: uv run pytest subprojects/docket/tests/test_config.py -k instruction -q && uv run pytest subprojects/docket/tests/test_checks.py -k 'threshold or re_dating' -q
---

**Problem.** Add instruction_stale_days to docket config, defaulting to 90, with synthetic-date tests so the advisory is tested before it first fires

`PL-T5K1` (the staleness advisory) has a threshold, and the threshold is the
load-bearing decision rather than an implementation detail — because it decides
whether the advisory is ever tested before it matters.

**Why it matters.** The oldest dated assertion in the instruction set is 21 days
old, measured 2026-09-21. At a 180-day threshold the advisory surfaces **zero
entries today and first fires in roughly 159 days** — dormant until spring, then
firing for the first time, untested, against assertions nobody remembers
writing, in a session with no idea what it is for. That is the shape of a
mechanism that is discovered to be broken at exactly the moment it was built to
help.

**Decision (project owner, 2026-09-21, ratified, over 180 days).** Default
`instruction_stale_days` to **90**, not 180. It first fires in roughly 69 days,
while the assertions are recent enough that the project owner can judge the
output quickly — and that first firing is the validation run. Raise it once the
advisory has been seen to name the right things.

**Design.** A field on the config dataclass beside `untriaged_stale_days: int =
14` in `subprojects/docket/src/docket/config.py`, read the same way and parsed
by the same loader. Nothing new in shape.

**Tested before it can fire, which is the point of filing this separately.**
The tests inject synthetic dates rather than waiting for the tree to age, so
both the past-threshold and the nothing-past-threshold branches are exercised
now. Without that, the first real evidence the advisory works arrives 69 days
after it merges.

**Done when.** `instruction_stale_days` is a configurable field defaulting to 90,
`PL-T5K1`'s advisory reads it, and tests using synthetic dates cover both a tree
with entries past the threshold and one with none.
