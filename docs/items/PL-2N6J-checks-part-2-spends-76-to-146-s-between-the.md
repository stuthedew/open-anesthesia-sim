---
id: PL-2N6J
title: checks-part-2 spends 76 to 146 s between the start of its pytest step and pytest's session header, against 33 to 44 s in checks-part-1 on the same image; find what the first uv run or pytest start-up does there
priority: P3
effort: S
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-10-18
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

**Next steps.** Read the `#1615` run's logs for both parts. Compare the
step's start with the header line, with `8 workers [N items]` and with the
first result line. If collection ends at about the same time in both parts,
the extra wait is part 2's costly tests running first. That is test work for
`PL-ZWQS`'s balance, not start-up, and this item closes on that finding. Then
decide whether to keep `PYTHONUNBUFFERED`, which makes CI's timestamps true
for every later timing, or revert it. If collection itself is slower in part
2, find what part 2's workers do differently during collection.

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
