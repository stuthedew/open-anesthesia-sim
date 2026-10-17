---
id: PL-YY32
title: Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline
priority: P2
effort: S
status: done
classes: infra
feature: friction-batch
touches: tools/main_ci_status.py, .claude/hooks/docket-digest.sh, tests/unit/test_main_ci_status.py, docs/apparatus.md
added: 2026-10-17
closed: 2026-10-17
pr: 1503
payoff: the session-start digest says when CI's pytest step has drifted from its baseline, so a slowdown like October's threefold growth is read at session start instead of noticed by feel weeks later
verify: grep -q 'pytest' tools/main_ci_status.py && grep -q 'baseline' tests/unit/test_main_ci_status.py
---

**Problem.** Nothing reads CI's pytest step time against a baseline, so the checks job grew from 144-359 s on 2026-09-28 to about 9 minutes by 2026-10-17 and was noticed by feel, as PL-H9KW: the session-start digest prints the step's recent median beside the recorded baseline

**Why it matters.** `main` refuses a branch that is not up to date, so every minute of the `checks` job is a minute for `main` to move under an armed pull request, and the job runs on every push to every pull request and every merge. The pytest step was 48 s on 2026-09-05, 144-359 s on 2026-09-28 (`PL-4Z5Y`), and about 9 minutes, 82% of the job, on 2026-10-17 (`PL-H9KW`). Nothing read the trend: `tools/main_ci_status.py` reads the latest run's conclusion for the red-main line and nothing reads a step's duration. The regression was found by feel three weeks in, which is the detection half `CLAUDE.md` § "Prefer deterministic tooling" says belongs in code.

**Done when.** The session-start digest carries one line giving the pytest step's median over the last N successful `checks` runs beside the baseline recorded for it, from the Actions API through the module that already owns that read (`tools/main_ci_status.py`), declining in words where the API cannot be read rather than printing a stale figure; the baseline lives in one place and is named; a unit test pins the computation and the declined path; the line is silent while the median sits within an agreed band of the baseline, so it earns its place by firing only on drift (project owner, 2026-10-17, ratified, over a ranking field for recurring costs). N and the band are the implementing session's call and are written into this brief.

**N and the band, chosen 2026-10-17.** N is 5 (`PYTEST_RUNS`), the band is 0.5 to 1.3 times the baseline (`PYTEST_BAND`), and the baseline is 470 s (`PYTEST_BASELINE_S`), all three in `tools/main_ci_status.py`. A run counts when its conclusion is `success`, so its pytest step ran to the end. The measurements behind them, over `main`'s 100 successful push runs #4906 to #5440 (2026-10-11 to 2026-10-17):

- The step's median time was 471.5 s.
- About a third of the runs land on a runner that takes about 0.57 of the others' time. The jobs payload names no machine type, so that cause is inferred.
- The median of five consecutive runs ranged from 0.59 to 1.16 times 471.5 s, so the band stays silent on all 96 such windows. A median of three reached 0.50 once.
- Read on every fourth run since 2026-09-15, a baseline set on 2026-09-16 (123 s) would have crossed 1.3 times on 2026-09-23, at run #2879. `PL-H9KW` was filed 24 days later.

The line costs five more requests at each session start, sent at once on threads, which added 0.6 s from a cloud container. `PL-H9KW`'s two test-time changes (#1486 and #1487) merged before the baseline was measured, so the last 16 of its 100 runs came after them. Their median was 502.5 s, 1.07 times the baseline, against 467.5 s for the 84 runs before them, so the baseline needs no new measurement for that fix. `PL-ZJRQ` was captured on the opposite reading and is dropped for this reason.

**Generator check.** The first shape in `.claude/rules/apparatus-standard.md` § "Read the fact from its record": nobody records the fact. CI's pytest step has a duration on every run of `quality.yml`, and nothing reads it against a baseline, so the step grew about threefold between 2026-09-28 and 2026-10-17 before `PL-H9KW` was filed by feel. No head's `misread:` states what a CI step costs per run - `PL-XBV4` is about the freshness of what a command read, `PL-0HPV` about which checks each gate runs, neither about their cost - and no second item misreads it, so this is a one-off and not a re-entry: `PL-H9KW` is the symptom, and the record this item writes is what would have found it.
