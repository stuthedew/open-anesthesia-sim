---
id: PL-6Y11
title: Cut v0.6.22 from the 45 items finished since v0.6.21
status: done
resource: release-train
added: 2026-11-23
closed: 2026-11-23
pr: 2278
verify: grep -qF '## Current baseline: v0.6.22' ROADMAP.md
---

**Problem.** Cut v0.6.22 from the 40 items finished since v0.6.21

**Why a patch.** `bin/docket status` suggested 0.7.0, because Gate 3 has
cleared and all 19 Required scope ids have closed. v0.7.0 is cut only at the
project owner's word after his test drive of `main`, so this is the next free
patch, as for v0.6.20 and v0.6.21 (`PL-49J8`).

**What was measured.** `src/anesthesia_sim/core/` moved from `0c045e7` to
`1e074b0`, in one comment in `supported_ranges.py` (`#2256`).
`uv run python tools/ast_identity.py v0.6.21 HEAD src/anesthesia_sim/core
src/anesthesia_sim/data` exited 0: no code moved in 42 files. `app/` moved a
lot, so the trajectories were compared anyway, with
`/mnt/project-files/release-trajectory/whole_second_traj.py` on each tree
(`git archive` of `v0.6.21` and of this cut's base, `TRAJ_JOBS=4`) and
`whole_second_compare.py`. The result is in
`/mnt/project-files/release-trajectory/v0.6.22-against-v0.6.21.txt`: 10,935
per-minute samples and 72 hourly samples identical, 174,960 and 1,152
formatted strings identical, and all 271 halts at the same instant.

**Tag span.** `#2247`, `#2248`, `#2251` and `#2252` are ancestors of
`v0.6.21` (`git merge-base --is-ancestor`), so v0.6.21's notes gain an
"also inside this tag's span" section naming `PL-SGBT`, `PL-8LDF`, `PL-41YP`,
`PL-W7HW` and `PL-V9KN`. `PL-YZ9L`'s `#2273` is in this cut's tree but its
item is still open, so this cut does not describe it.

**Inflow.** The cut reported one P1 workflow-lane apparatus filing in
2026-11-16..11-22 that PL-04KR did not expect, and no item named that week,
so one was filed under `convergence-visibility`.

**Re-cuts.** `main` moved five times while the cut was checked: `#2268`
(`PL-JP7P`, a deferred Gate 3 entry, `docs/INTERFACE.md`'s figures), `#2275`
(`PL-6XPZ`, `PL-92XM`, the control-change record's width in `app/`), `#2254`
(`PL-33CG`, the mutation check) with `#2279` (`PL-S5JJ`, `PL-SLFT`, a
docstring in `core/rounding.py` and the Yasuda source notes in the three agent
files), `#2269` (`PL-XWCH`, plain-words failure banners, which changed
`app/formatting.py`) after the closed cut was pushed, and `#2276` (`PL-HXSD`,
the hover box), which the armed-branch workflow merged into the branch after
it was armed. Auto-merge was disarmed so the tag would not land on a table
with the wrong `src/` hash. Each time the cut was undone (by a commit once it
was pushed), `main` merged and the cut run again: 37 items became 45, Gate 3's
cleared count 190 became 191. The tree after `#2275` and the tree after
`#2269` (`src/` at `073ca88`) were each recorded again and compared with
v0.6.21, with the same result. `#2276` changed only `app/qt_chart.py`'s hover
box placement and a comment in `app/theme.py`, which no recorded readout
reads, so that tree was not recorded again. `#2279` changed no code
(`tools/ast_identity.py` exit 0, only docstrings and comments in `core/`), and
a field-by-field comparison of the three agent files against v0.6.21 found
only the `note` of one source in each, so no stored value changed.

**Features.** `bin/docket feature --similar`'s highest pair scored 0.36
(`owner-ask-by-state` and `review-hold`); no pair is one goal, so none was
merged. The cut completes four features: `decision-ownership`,
`every-view-in-run-state-tests`, `model-claims-held-by-tests` and
`review-hold`.

