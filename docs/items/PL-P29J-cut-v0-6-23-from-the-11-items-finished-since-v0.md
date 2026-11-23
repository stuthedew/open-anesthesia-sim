---
id: PL-P29J
title: Cut v0.6.23 from the 11 items finished since v0.6.22
status: done
feature: release-process
resource: release-train
added: 2026-11-23
closed: 2026-11-23
pr: 2290
verify: grep -qF '## Current baseline: v0.6.23' ROADMAP.md
---

**Problem.** Cut v0.6.23 from the 11 items finished since v0.6.22

**Why a patch.** `bin/docket release --dry-run` suggested 0.7.0, because Gate 3
has cleared and all 19 Required scope ids have closed. v0.7.0 is cut only at
the project owner's word after their test drive of `main`, so this is the next
free patch, as for v0.6.20 to v0.6.22 (`PL-49J8`). The occasion is
`replay-findings` finishing with `#2289`.

**What was measured.** `src/anesthesia_sim/core/` (`e63728e`),
`src/anesthesia_sim/data/` (`056f3e7`) and `tests/reference/` (`2e5f2d7`) are
the same trees at `v0.6.22` and at this cut (`git rev-parse`), so no model code
or stored value moved. `src/` moved only in `app/` (16 files), and the run's
controller and formatters are there, so the trajectories were compared anyway,
with `/mnt/project-files/release-trajectory/whole_second_traj.py` on each tree
(`git archive` of `v0.6.22` and of this cut's base `489d0992`,
`TRAJ_JOBS=2`) and `whole_second_compare.py`. The result is in
`/mnt/project-files/release-trajectory/v0.6.23-against-v0.6.22.txt`: 10,935
per-minute samples and 72 hourly samples identical, 174,960 and 1,152
formatted strings identical, and all 271 halts at the same instant.

**Tag span.** Every cited pull request, `#2280` to `#2289`, is on `main` after
`v0.6.22` (`git log v0.6.22..HEAD`), so v0.6.22's notes need no pointer lines.
`tools/pr_body_check.py` found no squash commit that lost its body.

**Inflow.** The cut reported the one P1 workflow-lane apparatus filing in
2026-11-16..11-22 that PL-04KR did not expect. `PL-NJ54`, filed at v0.6.22's
cut, already names that week, so no new item was filed.
