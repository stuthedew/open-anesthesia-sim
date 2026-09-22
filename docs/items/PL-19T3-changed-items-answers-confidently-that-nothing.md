---
id: PL-19T3
title: changed_items answers confidently that nothing changed when run outside a git repository, because git diff exits 1 there and _run_git reads exit 1 as an answer, where git tag --list exits 128 and declines
priority: P3
effort: S
status: ready
classes: defect
feature: evidence-declines
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-22
payoff: a docket read taken outside a checkout says it could not answer, instead of telling the verify replay that the branch changed no item
verify: grep -q 'def test_changed_items_declines_outside_a_repository' subprojects/docket/tests/test_vcs.py
---

**Problem.** changed_items answers confidently that nothing changed when run outside a git repository, because git diff exits 1 there and _run_git reads exit 1 as an answer, where git tag --list exits 128 and declines

**Found closing `PL-ZPDM`, 2026-09-22, and it is the residue of that item.**
`tags` and `changed_items` both carry a `declined` channel now, and one
environment still splits them:

| Where | `git tag --list` | `git diff --name-only BASE...HEAD` |
| --- | --- | --- |
| inside a repository, base unresolvable | exit 0, answer | exit **128**, silence - declines |
| outside a repository | exit **128**, declines | exit **1**, "error: Could not access" - read as an answer |

`_run_git` classifies exit 1 as git answering no, which is right for the case
the rule was written for - `rev-parse --verify --quiet` on a ref that is not
there - and wrong here: there is no branch outside a repository, so "this
branch changed no item" is not a weaker truth but a different claim. The read
returns `known=True` and an empty set, which is the collapse
`.claude/rules/apparatus-standard.md`'s floor refuses.

**The sweep cannot see it**, which is why it is worth an item rather than a
line: `test_vcs_silence.py` runs every read against a real repository and
silences one call at a time, so an environment that has no repository at all is
outside its design.

**Low reach, and the cheap fix may be elsewhere.** Nothing in this project runs
`docket check --verify-base` outside a checkout, so the cost today is the claim
rather than a wrong decision taken from it. Two candidate routes, and the item
is which: classify `git diff`'s exit 1 by whether the command was a diff of
revisions (where git exits 1 only on error, `--exit-code` not being passed) or
probe the repository once per read and decline everything on the answer.

**Reproduced 2026-09-22 (`PL-14QR`, triage)**, from an empty directory outside any
repository. `vcs.changed_items(<dir>, "origin/main")` returned
`ChangedItems(identifiers=frozenset(), declined='')`, which is an answer. On the
same directory, `vcs.tags(<dir>)` declined, naming `git tag --list` as the
question git did not answer.

**Why it matters.** An empty, undeclined `ChangedItems` says the branch changed
no item. That set is what `docket check --verify-base` narrows its replay by,
so a read that could not be taken reaches the replay as a confident "nothing".
Reach is low today, since nothing runs it outside a checkout. But two reads
beside each other disagree about the same environment, and the next caller
inherits whichever one it happens to pick.

**Done when.** `changed_items` declines outside a repository, by either route
above, and a test in `subprojects/docket/tests/test_vcs.py` holds it from a
directory that is in no repository at all.
