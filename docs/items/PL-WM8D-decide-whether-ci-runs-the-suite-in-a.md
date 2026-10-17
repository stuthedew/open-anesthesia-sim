---
id: PL-WM8D
title: Decide whether CI runs the suite in a randomized order on a schedule: pytest-randomly in the dev group, -p no:randomly in pyproject's addopts, and a weekly drift.yml run seeded by the date, split from PL-75D9
priority: P3
effort: S
status: dropped
classes: test, infra
feature: test-effectiveness-measurement
touches: pyproject.toml, uv.lock, .github/workflows/drift.yml
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-17
reason: A duplicate. The project owner approved PL-75D9's randomized-order job as part of PL-75D9 on 2026-10-17 (recorded on #1497), which this split had not seen, so the job stays in PL-75D9.
---

**Problem.** CI never runs the suite in a randomized order, so a test that
passes only when it runs after another is never exercised. `PL-75D9`'s audit
measured no order dependence today: 5519 of 5519 tests passed with
pytest-randomly at seeds 12345 and 271828, in reverse order, and in a single
process. `.github/workflows/quality.yml` and the `Makefile` run
`-n 2*cpu --dist worksteal`, which gives each worker a contiguous slice, so
only a dependence across a slice boundary can surface. pytest-randomly is in
neither `pyproject.toml` nor `uv.lock`. This item is step 2 of `PL-75D9`'s
recommended work, split off at triage on 2026-10-17 because it adds a
dependency and a CI job, while step 1 is a simulator test.

**Why it matters.** In Python, order dependence caused 59% of 7571 flaky
tests in one large study (Gruber et al., ICST 2021,
doi:10.1109/ICST49551.2021.00026). Here a new one would surface as an
unrelated pull request going red, which costs a session a diagnosis, or as a
spurious result in a mutation run, which uses a fixed order.

**Decision needed.** Whether to add a scheduled randomized-order run, as
`PL-75D9` proposed: pytest-randomly in the dev group, `-p no:randomly` in
`pyproject.toml`'s `addopts` so every other run keeps its fixed order, and
`-p randomly --randomly-seed=$(date +%Y%m%d)` in a weekly job in
`.github/workflows/drift.yml`, which already runs on a schedule. A red run
names its seed, so it reproduces exactly. The opt-out has to be in `addopts`:
on two command lines alone, every other invocation would shuffle, including
sessions' own `uv run pytest` runs.

**Recommendation:** add it. The cost is one dev dependency, one `addopts`
flag and one weekly job in an existing workflow, with no time added to any
pull request. Its output is a seed that reproduces a failure exactly, which is
cheaper than diagnosing the same dependence when it first turns an unrelated
pull request red. The reason it is put to the owner is the new dependency and
CI job, the increase in complexity `CLAUDE.md` asks the owner to weigh. It is
not the generator pause, which is not in force: the one live head on
2026-10-17, `PL-X7D5`, is in the product lane.

**Done when.** The owner has decided, and if the answer is yes, a weekly
scheduled job runs the suite in a seeded random order while every other run
keeps its fixed order.

**Generator check.** A one-off. The fact misread is that the suite has a test
order nobody chose, and no generator head states it; nothing in the store
re-enters it.
