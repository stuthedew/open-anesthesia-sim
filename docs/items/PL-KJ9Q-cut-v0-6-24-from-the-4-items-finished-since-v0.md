---
id: PL-KJ9Q
title: Cut v0.6.24 from the 4 items finished since v0.6.23
status: untriaged
feature: release-process
resource: release-train
added: 2026-11-23
---

**Problem.** Cut v0.6.24 from the 4 items finished since v0.6.23

**Why a patch.** `bin/docket release --dry-run` suggested 0.7.0, because Gate 3
has cleared and all 19 Required scope ids have closed. v0.7.0 is cut only at
the project owner's word after their test drive of `main`, so this is the next
free patch, as for v0.6.20 to v0.6.23 (`PL-49J8`). The occasion is
`documentation-standard` finishing with `#2295` and `tests-detect-wrong-values`
finishing with `#2292`.

**What was measured.** `src/anesthesia_sim/core/` (`e63728e`),
`src/anesthesia_sim/data/` (`056f3e7`) and `tests/reference/` (`2e5f2d7`) are
the same trees at `v0.6.23` and at this cut (`git rev-parse`), so no model code
or stored value moved. `src/` moved only in `app/qt_chart.py` (`#2292`), where
the two legends now build each reported entry from the drawn label and swatch.
The trajectories were compared anyway, with
`/mnt/project-files/release-trajectory/whole_second_traj.py` on each tree
(`git archive` of `v0.6.23` and of this cut's base `a73565be`, `TRAJ_JOBS=2`)
and `whole_second_compare.py`. The result is in
`/mnt/project-files/release-trajectory/v0.6.24-against-v0.6.23.txt`: 10,935
per-minute samples and 72 hourly samples identical, 174,960 and 1,152
formatted strings identical, and all 271 halts at the same instant.

**Tag span.** Every cited pull request (`#2281`, `#2292`, `#2293`, `#2295`) is
on `main` after `v0.6.23` (`git merge-base --is-ancestor`), so v0.6.23's notes
need no pointer lines. `tools/pr_body_check.py` found no squash commit that
lost its body.

**Inflow.** The cut reported the one P1 workflow-lane apparatus filing in
2026-11-16..11-22 that PL-04KR did not expect. `PL-NJ54`, filed at v0.6.22's
cut, already names that week, so no new item was filed.

**Features.** `bin/docket feature --similar` paired no two features above a
0.36 word overlap, and no pair read as one goal, so none were merged.
