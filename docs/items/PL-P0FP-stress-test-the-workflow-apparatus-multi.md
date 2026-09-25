---
id: PL-P0FP
title: Stress-test the workflow apparatus: multi-session simulation, adversarial inputs to the prose-reading checks, duplicate-definition audit and inflow forensics, and record what makes its defect inflow multiple per day
status: done
feature: workflow-stress-2026-09
touches: docs/items, docs/stress-2026-09-25/evidence.tar.gz
added: 2026-09-25
closed: 2026-09-25
verify: bin/docket feature exact-gates && bin/docket feature one-snapshot && bin/docket feature claim-integrity && bin/docket feature one-answer && bin/docket feature workflow-stress-2026-09 && grep -q '^root-cause-of: ' docs/items/PL-GPJ7-*.md && grep -q '^root-cause-of: ' docs/items/PL-XBV4-*.md && grep -q '^root-cause-of: ' docs/items/PL-PVW2-*.md && bin/docket show PL-2866
---

**Problem.** Apparatus defects like PL-YSMV (a prose-reading gate refuses correct prose) and PL-X3NY (stranded cannot tell in-flight pull-request work from abandoned) arrive multiple times a day. The owner asked, 2026-09-25, for a stress test run without affecting `main`, and for what would make such defects occasional.

**What was run.** Four independent probes, each saved as a reproducible script in the evidence archive:

- **Multi-session simulation** (`sim/harness.py`): a bare origin, a clone playing GitHub (squash-merge, branch deletion, close), N session clones on a world clock, pull-request state faked through `open_pull_requests_command`; 11 invariants, 19 scenarios, 6 seeded random runs of 30 steps. Eight violations: V1 late claim displaces a confirmed one (PL-ZLJ9), V2 unpushed claim exits 0 (PL-1X56), V3 working tree behind origin/main offers closed items (PL-Y48N), V4 failed fetch reported as a refresh (PL-8Z1T), V5 merged captures-only PR never recognised (PL-8BR0), V6 is PL-X3NY, V7 extends PL-QSGX (PL-D1P5), V8 claim refuses the harness's branch shape (PL-KX73).
- **Adversarial prose** (`fuzz/`): correct-but-tricky prose injected into real documents, each check run as `make check` runs it. 35 false refusals reproduced across 9 checks, every one from heuristic recognition in a hard gate; filed under PL-GPJ7.
- **Duplicate definitions and cross-command consistency** (`dupes/`): nine questions answered by two or more disagreeing implementations, one of them the protected-path audit (PL-KR69, reproduced twice); filed under PL-PVW2 and PL-XBV4.
- **Inflow forensics** (`inflow/`):

Measured over the store on origin/main, 2026-09-15..25, by the inflow scripts in the evidence archive:

- **Inflow is at its peak, not declining.** 169 apparatus defects filed in the 7 days to 09-24, against 72 in the 7 days to 09-12; the open apparatus backlog has held at 164-176 since 09-16, net zero only because closures rose to match. 20 of 35 recorded generators are drained.
- **Discovery is internal.** Of 226 apparatus defects, 193 (85%) were found while working another apparatus item, 12 (5%) by main going red, 7 (3%) during product work - against 72 simulator items closed in the same window, about 1 apparatus defect per 10 product items.
- **Fixing spawns.** 0.66 new apparatus items per apparatus item closed (0.78 for 09-15..19, 0.59 for 09-20..25).
- **Mechanism classes.** Distributed-state inference 26%, heuristic text recognition 14% plus `verify:`-as-proof 8%, two definitions of one predicate 14%, statement drift 7.5%, output/UX 6.6%, git plumbing 5.8%, other 17%. 41 of 226 had a close second class.
- **Hot files.** README 54 defect items, cli.py 50, vcs.py 45, render.py 37, verify.py 36 (its diff-text integrity checks alone: 19 items in 10 days), doc_check.py 28.

**Why it matters.** The three largest classes are each one mechanism, and each was being paid one item at a time.

**Done when.** The findings are in the queue under the features `exact-gates`, `one-snapshot`, `claim-integrity`, `one-answer` and `workflow-stress-2026-09`, the three heads carry `root-cause-of:`, and the plan decision stands as its own item.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn`.
