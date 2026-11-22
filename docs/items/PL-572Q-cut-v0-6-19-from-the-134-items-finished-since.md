---
id: PL-572Q
title: Cut v0.6.19 from the 134 items finished since v0.6.18
status: done
resource: release-train
added: 2026-11-22
closed: 2026-11-22
pr: 2209
verify: grep -qF '## Current baseline: v0.6.19' ROADMAP.md
---

**Problem.** Cut v0.6.19 from the 134 items finished since v0.6.18

**The cut, 2026-11-22.** The version is 0.6.19 and the notes are in
`docs/releases/v0.6.19.md`, with 134 items stamped. The first cut ran on a
shallow clone and asked for no pointer lines in v0.6.18's notes. After `git
fetch --unshallow`, `tools/doc_check.py` named `#2103` and `#2118` as inside
v0.6.18's tag span, and v0.6.18's notes now carry them under "also inside this
tag's span". `PL-49J8` is filed for the version guess that stalled this
release: the dry run's guess was 0.7.0, and the survey said "No release to
offer".

**Trajectories against v0.6.18, 2026-11-22.** `core/` moved, so both tags were
run with `whole_second_traj.py` and compared with `whole_second_compare.py`,
in the project's shared folder `release-trajectory/`. The output is
`release-trajectory/v0.6.19-against-v0.6.18.txt` there. Both scripts gained a
guard in this session: `RunDefinition.state_at` is gone since `PL-Z6C8`, so the
canonical reading is skipped where a tree lacks it, and the comparison of the
stepped readings, halts and 24-hour runs is unchanged. Results:

1. Stepped readings each minute: 10,935 samples, largest fraction difference
   1.4e-13 atm, 1.4e-11 of the state's largest fraction.
2. Readout strings: 543 of 174,960 differ, all field 12 (the delivered agent
   volume, shown to 0.1 L), each by one 0.1 L step.
3. Halts: 103 at the same instant, 168 later by 0.1 to 0.9 s, the new tree's
   halt always on a whole second. No halt count differs.
4. 24-hour runs: 72 samples, largest difference 2.3e-12 atm, no readout
   differs.
5. No crash and no other problem in either tree.

`#2180` measured the same comparison against `main` at `c478e2b18` and found
461 delivered-volume readouts that differ. This comparison finds 543, and the
82 more were not traced to a cause.
