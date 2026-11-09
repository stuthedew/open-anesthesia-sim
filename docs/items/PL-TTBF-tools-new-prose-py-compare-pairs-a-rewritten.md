---
id: PL-TTBF
title: tools/new_prose.py --compare pairs a rewritten section by diff hunk, so a rewrite that adds subheadings shows growth the text did not have: PL-J37P's 'Why the readouts show two decimals' read 854 to 1,050 words while the next subsection read 2,093 to 1,561
priority: P1
effort: S
status: ready
classes: defect
feature: copy-editor
touches: tools/new_prose.py, tests/unit/test_new_prose.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: --compare arrived in 5df31d49 (PL-JP8X); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
payoff: a session's growth figures for a restructured section are true, so the facts it names for grown passages, and PL-J1ZM's next measurement, rest on real growth
verify: grep -q 'def test_a_passage_under_a_heading_the_base_lacks' tests/unit/test_new_prose.py
---

**Problem.** tools/new_prose.py --compare pairs a rewritten section by diff hunk, so a rewrite that adds subheadings shows growth the text did not have: PL-J37P's 'Why the readouts show two decimals' read 854 to 1,050 words while the next subsection read 2,093 to 1,561.

**Evidence.** Before `PL-J37P` (#2022), § "Displayed precision" had no subheadings, and the rewrite gave it eleven. `python3 tools/new_prose.py --base 53cd01239^ --compare`, run in a worktree at 53cd01239, labels each diff hunk with the new subheading and counts the hunk's old side as the passage's words on the base. So "Why the readouts show two decimals" reads 854 to 1,050 words, 196 more, and "The MAC multiple's resolution" reads 2,093 to 1,561, while the section as a whole went from 8,142 words to 6,732. Text moved between hunks reads as growth in one and a cut in the other.

**What a fix needs.** Where the base has no heading that matches the new one, the tool should compare the enclosing section that exists on both sides, or say that it could not pair the passage. It should not print a figure that looks like a measurement.

**Checked 2026-11-09:** In a worktree at 53cd01239 with today's `tools/new_prose.py` copied in, `python3 tools/new_prose.py --base 53cd01239^ --compare` still prints "Why the readouts show two decimals ... 854 words on 53cd01239^, 1050 now, 196 more" and "The MAC multiple's resolution ... 2093 words on 53cd01239^, 1561 now, 532 fewer". `changed_passages` still names each passage after the nearest heading on the new side only.

**Why it matters.** Close-out step 8 asks the writer to name, in the pull request body, the facts that each grown passage adds. On a restructured section the tool reports growth and cuts that did not happen. The writer then either names facts for growth that is not there or learns to ignore the figures, and `PL-J1ZM`'s next measurement reads the same figures.

**Done when.** On a rewrite that adds headings the base lacks, `--compare` compares the enclosing section that exists on both sides, or says that it could not pair the passage. A test built from that case asserts it.

**Generator check.** Part of the fix for the live head `PL-J1ZM` (sessions over-explain), which is blocked on it; not a member of its `root-cause-of`. The fact misread here is which text on the base a rewritten passage replaced. No head states it, so it is a one-off, and the pause on new workflow mechanisms does not hold it, because it fixes that generator.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, `tools/new_prose.py` had no `--compare` and no `changed_passages`. Both arrived in 5df31d49 (`PL-JP8X`, #2014, 2026-11-03), so this is a new problem. It is deferred with `PL-J1ZM`, which waits on it.
