---
id: PL-YY32
title: Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline
status: untriaged
feature: friction-batch
added: 2026-10-17
verify: grep -q 'pytest' tools/main_ci_status.py && grep -q 'baseline' tests/unit/test_main_ci_status.py
---

**Problem.** Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline

**Why it matters.** `main` refuses a branch that is not up to date, so every minute of the `checks` job is a minute for `main` to move under an armed pull request, and the job runs on every push to every pull request and every merge. The pytest step was 48 s on 2026-09-05, 144-359 s on 2026-09-28 (`PL-4Z5Y`), and about 9 minutes, 82% of the job, on 2026-10-17 (`PL-H9KW`). Nothing read the trend: `tools/main_ci_status.py` reads the latest run's conclusion for the red-main line and nothing reads a step's duration. The regression was found by feel three weeks in, which is the detection half `CLAUDE.md` § "Prefer deterministic tooling" says belongs in code.

**Done when.** The session-start digest carries one line giving the pytest step's median over the last N successful `checks` runs beside the baseline recorded for it, from the Actions API through the module that already owns that read (`tools/main_ci_status.py`), declining in words where the API cannot be read rather than printing a stale figure; the baseline lives in one place and is named; a unit test pins the computation and the declined path; the line is silent while the median sits within an agreed band of the baseline, so it earns its place by firing only on drift (project owner, 2026-10-17, ratified, over a ranking field for recurring costs). N and the band are the implementing session's call and are written into this brief.
