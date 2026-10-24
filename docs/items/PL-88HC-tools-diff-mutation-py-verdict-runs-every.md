---
id: PL-88HC
title: tools/diff_mutation.py --verdict runs every mutant of each changed function although only mutants on changed lines can refuse, so verify --self spent 36 minutes on PL-2TZT's 340-mutant batch; select the mutants of changed lines before mutmut runs
priority: P2
effort: M
status: ready
classes: session-cost
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md
added: 2026-10-24
payoff: a review of a branch with a large changed function no longer waits on mutants that cannot change verify's verdict; #1676's run took 36 minutes
verify: grep -q 'def test_the_verdict_runs_only_the_mutants_of_changed_lines' tests/unit/test_diff_mutation.py
---

**Problem.** tools/diff_mutation.py --verdict runs every mutant of each changed function although only mutants on changed lines can refuse, so verify --self spent 36 minutes on PL-2TZT's 340-mutant batch; select the mutants of changed lines before mutmut runs

**Found 2026-10-24 while building `PL-CZXN`.** `verdict` in `tools/diff_mutation.py` counts only mutants on a line the branch changed, but `run` asks mutmut for every mutant of each changed function. `#1676`'s batch changed 16 functions holding 340 mutants and took 2,190 s on four cores, while another session's tests shared them. Only three of its six survivors were on changed lines. Choosing the mutants of changed lines before the run would need each mutant's line before mutmut runs it, which `mutmut show` gives one subprocess at a time and the generated `mutants/` files give all at once. The fixed cost, about five minutes of coverage collection, would remain.

**Why it matters.** Every `verify --self` and every delegated review of a branch that changes a mutated function pays for mutants that cannot change the verdict. That was 40 of the 445 merges on `main` from 2026-10-01 to 2026-10-24, by `PL-CZXN`'s count. On the largest batch, `#1676`, the run took 2,190 s for 340 mutants. This item does not touch the fixed cost of about five minutes, so the saving is small on the 37 of those 40 merges that had 200 mutants or fewer, and large on the few big batches. That is why it is not raised as friction that compounds: it is paid on about one merge in eleven, and on most of those the fixed cost it leaves in place is most of the run.

**Done when.** `tools/diff_mutation.py --verdict` asks mutmut to run only the mutants that change a line the branch changed. A mutant whose line cannot be placed before the run still runs, so it can still refuse. The verdict's `uncaught` and `undecided` lists are unchanged for every branch. A test shows that a mutant on an unchanged line of a changed function is not run. The note that names survivors on unchanged lines of a changed function goes with them, and the builder says in `docs/mutation-testing.md` whether `make mutate` without `--verdict` still runs whole functions for a reviewer.

**Generator check.** A one-off. It is a known cost of the tool `PL-CZXN` built, measured and recorded in that item's own brief when it closed, and not a misread fact: `run` selects by function because mutmut names its mutants by function, while `verdict` counts by line. No `reenters:`, because `PL-CZXN`'s done-when asked for the replacement check, not for its run time.
