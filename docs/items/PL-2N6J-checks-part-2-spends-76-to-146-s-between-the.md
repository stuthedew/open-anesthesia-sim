---
id: PL-2N6J
title: checks-part-2 spends 76 to 146 s between the start of its pytest step and pytest's session header, against 33 to 44 s in checks-part-1 on the same image; find what the first uv run or pytest start-up does there
priority: P3
effort: S
status: done
feature: ci-cost
milestone: v0.5.33
touches: .github/workflows/quality.yml
added: 2026-10-18
closed: 2026-10-19
pr: 1615
payoff: part 2 starts its tests 35 to 100 s sooner on most quality runs, so the run ends that much sooner
not-delegable: the cause can be found only by timing CI runs on GitHub, which no local command can do
---

**Tabled** (project owner, 2026-10-18, ratified, over chasing the cause now).
The gap costs about 35 to 100 s on most runs, and its cause is unknown. The
owner set the bar for CI work at low-hanging fruit, not a new problem to
troubleshoot, so this ranks `P3`. Pick it up only if CI time becomes a
problem again.

**Taken up** (project owner, 2026-10-18, ratified, over leaving it tabled).
`PL-ZWQS` found that part 2 finishes last on every run where both parts get
the same class of runner. The owner agreed to work this item first and then
re-measure the gap.

**Findings so far, 2026-10-18.**

- **Cold bytecode is not the cause.** A local timing on a 4-core container
  started pytest with all 8 workers and selected no tests. It took 38 to 41 s
  for either part, with or without `__pycache__` directories. Collection alone
  took 14 to 17 s, and cold bytecode added at most 3 s.
- **Locally, the header is not late.** In a full local run of part 2, pytest
  printed its session header and `created: 8/8 workers` 0.5 s after start. It
  printed `8 workers [5702 items]`, the end of collection, at 36 s. The first
  72 results arrived at 112 s, because part 2's first tests build the costly
  computations. The run took 290 s.
- **On CI, the log stamps the header at the end of collection.** In run
  39173547056, the header, `created: 8/8 workers` and `8 workers [N items]`
  all carry the same timestamp, in both parts. Part 2's header came 161 s
  after its step started, and part 1's came 49.5 s after. Part 2's first
  result line came 37 s after its header, and part 1's came 0.2 s after.
  Setting `CI=true` and `GITHUB_ACTIONS=true` locally did not delay the
  header. So it is not yet known whether part 2's 161 s is collection,
  buffering, or its first tests.
- **The measurement in flight.** Draft pull request `#1615` runs both
  pytest steps with `PYTHONUNBUFFERED=1`, so the log stamps each line when
  pytest prints it.

**The cause is part 2's costly tests, not start-up, measured 2026-10-19.**
`#1615`'s run 39178452962 ran both pytest steps with `PYTHONUNBUFFERED=1`.
Part 1 ran in `westus` and part 2 in `eastus`, on the same image and with 8
workers each. The times below are seconds from the start of the pytest step.

| Event | Part 1 | Part 2 |
| --- | --- | --- |
| Session header and `created: 8/8 workers` | 1.0 | 1.2 |
| End of collection, `8 workers [N items]` | 48.9 (3,779 items) | 39.2 (5,702 items) |
| First result line, `[  1%]` | 49.1 | 143.7 |
| Summary line | 230.1 | 354.8 |

- **Start-up and collection are not slower in part 2.** Both parts print the
  header within about 1 s. Collection ends at 39 to 49 s in both, and part 2
  was the faster of the two on this run.
- **The old logs were misleading.** Without `PYTHONUNBUFFERED`, the log
  stamped the header at the end of collection, or later. That is why part 2's
  header seemed to come 76 to 161 s after its step started.
- **The wait is part 2's costly tests.** Part 2's first 1% of results came
  104.5 s after collection ended, against 0.2 s in part 1. `tests/conftest.py`
  deals the costly computations to part 2 and puts them first, so all 8
  workers start by building them. After that, part 2 reached 50% about 65 s
  later.

So there is no start-up cost to remove. Part 2 runs longer because it holds
more pytest work: 354.8 s against 230.1 s here. Balancing that work is
`PL-ZWQS`'s next step, which re-measures the gap and moves ordinary tests to
part 1 if it is still more than 30 s.

**`PYTHONUNBUFFERED` stays.** It costs nothing measurable, and without it CI's
log timestamps are wrong for any later timing of the pytest steps. The comment
in `quality.yml` now says why it is there.

**Problem.** In `quality.yml`, `checks-part-2` waits much longer than
`checks-part-1` before pytest starts. The gap is measured from the pytest
step's `##[group]Run` line to pytest's `test session starts` header, which
pytest prints before it collects any tests. Six `main` push runs on
2026-10-18 (39089555634, 39087673393, 39086712437, 39083578852, 39086182821,
39081769574) show 76 to 78 s on fast runners and 141 to 146 s on slow ones in
part 2. Part 1 shows 33 to 44 s. Both parts used the same image
(`ubuntu-24.04`, version 20261012.334.1) and the same 8 workers.

The gap is not runner speed alone. In run 39087673393 both parts ran in
`centralus`, and part 2 still waited 77 s against part 1's 42 s. One
difference is that pytest is part 2's first `uv run`, while part 1 runs `uv
run ruff`, `uv run mypy` and `uv run python tools/ignore_check.py` before it.
This is a lead, not a measured cause. Cold bytecode compilation of the
installed packages on first import is another candidate.

**Why it matters.** Part 2 finishes last on 10 of the 12 `main` runs since
`#1519`, so about 35 to 100 s of its start-up is paid on almost every run's
wall time.

**Done when.** The extra start-up in part 2 is attributed to a named cause
from a timed CI run, and either removed or recorded here as not worth its
code.
