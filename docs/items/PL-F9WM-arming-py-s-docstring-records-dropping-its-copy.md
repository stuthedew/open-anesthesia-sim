---
id: PL-F9WM
title: arming.py's docstring records dropping its copy of vcs.RECORDS without the owner's ratification mark, and names 'the pinned tests, which name the directory' where the test that holds a widening names the held paths
priority: P3
effort: S
status: done
classes: docs
feature: one-source-of-truth
touches: subprojects/docket/src/docket/arming.py
added: 2026-10-24
closed: 2026-10-24
pr: 1747
payoff: a session reading the merge gate can see that the owner chose a single copy of the body-records directory, and what now holds a widening of it
verify: grep -q 'over restoring the copy that `PL-F6MM` kept' subprojects/docket/src/docket/arming.py
---

**Problem.** arming.py's docstring records dropping its copy of vcs.RECORDS without the owner's ratification mark, and names 'the pinned tests, which name the directory' where the test that holds a widening names the held paths

**Why it matters.** On 2026-09-26 the project owner ratified keeping a second copy of `docs/pr-bodies/` in `arming.py`, so that widening what arms on green would wait on their read (`PL-F6MM`). `PL-LGDV` (#1740) removed that copy on 2026-10-24, because since `PL-9JHM` an edit to both copies together waited on no read. A ratified decision is reopened by putting it back to the owner, and #1740 merged first. The owner then agreed on 2026-10-24 to keep the single copy. Without the mark, a later session reading the docstring cannot tell that the owner saw this. The docstring also said an edit to the module "waits on no read" and that "the pinned tests ... name the directory". Neither is accurate: `PL-9JHM` still holds an edit that changes a test pinning the module's answers, and the test that holds a widening names the held paths.

**Done when.** The docstring of `waits_on_read`'s caller in `arming.py` records the owner's 2026-10-24 ratification and names `test_arm_holds_for_a_read_a_path_on_the_owners_read_list` as what holds a widening.

**Generator check.** A one-off. It records a decision; no fact was misread.
