---
id: PL-TTBF
title: tools/new_prose.py --compare pairs a rewritten section by diff hunk, so a rewrite that adds subheadings shows growth the text did not have: PL-J37P's 'Why the readouts show two decimals' read 854 to 1,050 words while the next subsection read 2,093 to 1,561
status: untriaged
feature: copy-editor
added: 2026-11-04
---

**Problem.** tools/new_prose.py --compare pairs a rewritten section by diff hunk, so a rewrite that adds subheadings shows growth the text did not have: PL-J37P's 'Why the readouts show two decimals' read 854 to 1,050 words while the next subsection read 2,093 to 1,561.

**Evidence.** Before `PL-J37P` (#2022), § "Displayed precision" had no subheadings, and the rewrite gave it eleven. `python3 tools/new_prose.py --base 53cd01239^ --compare`, run in a worktree at 53cd01239, labels each diff hunk with the new subheading and counts the hunk's old side as the passage's words on the base. So "Why the readouts show two decimals" reads 854 to 1,050 words, 196 more, and "The MAC multiple's resolution" reads 2,093 to 1,561, while the section as a whole went from 8,142 words to 6,732. Text moved between hunks reads as growth in one and a cut in the other.

**What a fix needs.** Where the base has no heading that matches the new one, the tool should compare the enclosing section that exists on both sides, or say that it could not pair the passage. It should not print a figure that looks like a measurement.
