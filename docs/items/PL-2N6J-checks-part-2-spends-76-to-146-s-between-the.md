---
id: PL-2N6J
title: checks-part-2 spends 76 to 146 s between the start of its pytest step and pytest's session header, against 33 to 44 s in checks-part-1 on the same image; find what the first uv run or pytest start-up does there
status: untriaged
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-10-18
---

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
