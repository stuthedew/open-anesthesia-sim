---
id: PL-YY32
title: Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline
priority: P2
effort: S
status: ready
classes: infra
feature: friction-batch
touches: tools/main_ci_status.py, .claude/hooks/docket-digest.sh, tests/unit/test_main_ci_status.py
added: 2026-10-17
payoff: the session-start digest says when CI's pytest step has drifted from its baseline, so a slowdown like October's threefold growth is read at session start instead of noticed by feel weeks later
verify: grep -q 'pytest' tools/main_ci_status.py && grep -q 'baseline' tests/unit/test_main_ci_status.py
---

**Problem.** Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline

**Why it matters.** `main` refuses a branch that is not up to date, so every minute of the `checks` job is a minute for `main` to move under an armed pull request, and the job runs on every push to every pull request and every merge. The pytest step was 48 s on 2026-09-05, 144-359 s on 2026-09-28 (`PL-4Z5Y`), and about 9 minutes, 82% of the job, on 2026-10-17 (`PL-H9KW`). Nothing read the trend: `tools/main_ci_status.py` reads the latest run's conclusion for the red-main line and nothing reads a step's duration. The regression was found by feel three weeks in, which is the detection half `CLAUDE.md` § "Prefer deterministic tooling" says belongs in code.

**Done when.** The session-start digest carries one line giving the pytest step's median over the last N successful `checks` runs beside the baseline recorded for it, from the Actions API through the module that already owns that read (`tools/main_ci_status.py`), declining in words where the API cannot be read rather than printing a stale figure; the baseline lives in one place and is named; a unit test pins the computation and the declined path; the line is silent while the median sits within an agreed band of the baseline, so it earns its place by firing only on drift (project owner, 2026-10-17, ratified, over a ranking field for recurring costs). N and the band are the implementing session's call and are written into this brief.

**Generator check.** The first shape in `.claude/rules/apparatus-standard.md` § "Read the fact from its record": nobody records the fact. CI's pytest step has a duration on every run of `quality.yml`, and nothing reads it against a baseline, so the step grew about threefold between 2026-09-28 and 2026-10-17 before `PL-H9KW` was filed by feel. No head's `misread:` states what a CI step costs per run - `PL-XBV4` is about the freshness of what a command read, `PL-0HPV` about which checks each gate runs, neither about their cost - and no second item misreads it, so this is a one-off and not a re-entry: `PL-H9KW` is the symptom, and the record this item writes is what would have found it.
