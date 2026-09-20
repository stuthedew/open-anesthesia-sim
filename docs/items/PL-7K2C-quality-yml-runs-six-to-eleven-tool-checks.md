---
id: PL-7K2C
title: quality.yml runs six to eleven tool checks after the whole-store verify replay, so a replay failure skips contrast, import-boundary, core-vocabulary and glyph checks on that main commit entirely - moving the replay to the end of the job would cost nothing and close the gap
priority: P2
effort: S
status: ready
classes: defect, infra
touches: .github/workflows/quality.yml, tests/unit
added: 2026-09-20
payoff: a replay failure stops taking the contrast, import-boundary, core-vocabulary and glyph checks down with it, so a palette or layering regression is still caught on that main commit
verify: grep -rq 'def test_the_whole_store_replay_is_the_last_step_in_the_job' tests/unit
---

**Problem.** quality.yml runs six to eleven tool checks after the whole-store verify replay, so a replay failure skips contrast, import-boundary, core-vocabulary and glyph checks on that main commit entirely - moving the replay to the end of the job would cost nothing and close the gap

**Why it matters.** The replay is the most expensive and the most failure-prone
step in the job, and everything a reordering would protect is cheap and
deterministic. A `main` commit whose replay fails therefore ships with the
contrast audit, the import-boundary check, the core-vocabulary check and the
glyph check never having run against it - so a palette regression or a layering
violation lands unnoticed behind an unrelated red, and the branch that fixes
the replay is the first thing to report it, against a tree where it is no
longer new. `CLAUDE.md` reserves this shape as a defect in the check rather
than in the code: a gate that stops reporting the moment an earlier gate fails
is a gate whose coverage is conditional on something it does not control.

**Reproduced 2026-09-20.** `.github/workflows/quality.yml` runs `verify replay,
the whole store` at line 287 with one further named step after it in the same
job, and the tool checks that precede the replay are the ones a replay failure
does not skip. Ordering is the whole of the fix: no step depends on the
replay's result.

**Done when.** The whole-store verify replay is the last step of its job, every
tool check runs ahead of it, and a test under `tests/unit/` reads
`quality.yml` and fails if any named step follows the replay.
