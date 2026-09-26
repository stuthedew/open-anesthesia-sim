---
id: PL-139L
title: vcs reads git's subject-bearing log output with str.splitlines, which also breaks at \x0b, \x0c, \x1c-\x1e, \x85 and \u2028, so a commit whose subject carries one is split and misread
priority: P3
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-24
closed: 2026-09-26
payoff: a commit subject holding a stray form feed or line separator can no longer make docket report work in flight, landed or merged that is not
verify: grep -q 'def test_a_line_separator_inside_a_subject_does_not_start_another_subject' subprojects/docket/tests/test_vcs.py
---

**Problem.** vcs reads git's subject-bearing log output with str.splitlines, which also breaks at \x0b, \x0c, \x1c-\x1e, \x85 and \u2028, so a commit whose subject carries one is split and misread

**Premise re-checked at triage, 2026-09-24.** A throwaway repository was made
whose commit subjects hold `\x0c`, U+2028 and `\x0b`. Read through the real
`vcs._landed_since` and `vcs.merged_pull_requests`, it produced ids and pull
request numbers that no subject starts with. git 2.43 prints those characters
unchanged in `%s`. `str.splitlines` also breaks at U+2029, which the title
leaves out. Eight readers in `vcs.py` split subjects this way:

- `_unmerged_commits`
- `_landed_since`
- `merged_pull_requests`
- `_merges_naming`
- `change_landed`
- `_taken_on_base`
- `_duplicated_history`
- `filed_with_work`

**Why it matters.** Each of those feeds a verdict that other commands trust:
what is in flight, what has landed, and which pull request carried an item.
Each goes wrong silently. No subject carries such a character today, so the
risk is a paste rather than routine work, which is why this is P3.

**Done when.** All eight readers split git's output on `\n` only. A test in
`subprojects/docket/tests/test_vcs.py` pins a subject holding a form feed or
U+2028.

**Generator check.** The misread fact is where a line ends. `str.splitlines`
breaks at `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, U+2028 and U+2029 as well as
at newlines, but git and Python's tokenizer break only at newlines.

- `PL-PK4B` misreads the same fact.
- Six code sites already use `split("\n")` on purpose, beside comments naming
  `PL-3FYK`, `PL-0TD9`, `PL-JD4L` or `PL-4W2L`. None of those briefs mentions
  the hazard, so none of them is an item this fact produced.

That makes two items and no head. A third item would make one: 53 of the 115
`.splitlines()` calls under `subprojects/docket/src` and `tools/` split git
output or text that is parsed afterwards. That includes three tools that read
commit subjects: `branch_id_check.py`, `left_behind_check.py` and
`doc_check.py`.

**Worked.** Two of the eight readers the premise lists, `_unmerged_commits` and
`_taken_on_base`, no longer exist: `PL-FX5Q` deleted them with the claim
inference (#1016). So six changed: `change_landed`, `_landed_since`,
`_duplicated_history`, `merged_pull_requests`, `filed_with_work` and
`_merges_naming`. Only each one's subject-bearing read changed. Three reads
carry no subject and are unchanged: `change_landed`'s `diff --name-only` and
`merge-tree` reads, and `filed_with_work`'s `show --name-only` read. The last
is `PL-NK1L`, and the path side of this hazard is captured as `PL-PQ0R`. The
reason is written once, at `change_landed`, and the other five point to it.
There are six tests rather than one. The named test goes through a real
repository, runs once for each of the eight characters `str.splitlines` breaks
at and git does not, and reads `merged_pull_requests`. Each other reader has one
test of its own, on the fake git or scratch repository its existing tests use.
All thirteen cases fail with the old split.
