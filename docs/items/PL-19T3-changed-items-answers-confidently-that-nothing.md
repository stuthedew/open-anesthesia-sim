---
id: PL-19T3
title: changed_items answers confidently that nothing changed when run outside a git repository, because git diff exits 1 there and _run_git reads exit 1 as an answer, where git tag --list exits 128 and declines
priority: P3
effort: S
status: done
classes: defect
feature: evidence-declines
milestone: v0.5.7
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-09-22
closed: 2026-09-23
pr: 934
payoff: a docket read taken outside a checkout says it could not answer, instead of telling the verify replay that the branch changed no item
verify: grep -q 'def test_every_read_declines_from_a_directory_in_no_repository' subprojects/docket/tests/test_vcs_silence.py
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
no item. That set is what `docket check --verify-base` narrows its replay by.
Until `PL-9RFP`, a read that could not be taken reached the replay as a
confident "nothing". Reach is low today, since nothing runs it outside a
checkout. But two reads beside each other disagree about the same environment,
and the next caller inherits whichever one it happens to pick.

**The replay no longer takes this answer on its own (2026-09-23, `PL-9RFP`).**
`cmd_check` reads `verify.changed_paths` beside `changed_items`. Outside a
repository that read exits 129 and now declines, so the replay declines whole
and says why. `test_verify_base_outside_a_repository_declines_the_replay`
holds that; before, it asserted the narrowing this item describes. What is left
is `changed_items` itself answering `known=True` where it read nothing, for
the next caller that takes it alone. That still needs its own test, from a
directory in no repository, in `test_vcs.py`.

**Done when.** `changed_items` declines outside a repository, by either route
above, and a test in `subprojects/docket/tests/test_vcs.py` holds it from a
directory that is in no repository at all.

**Built 2026-09-23, by the first route, with the test moved to the sweep.**
`_run_git` now reads a `diff`'s exit 1 as a silence (`_asks_for_a_diff`),
beside `_asks_for_a_blob` carrying the opposite exception. Three measurements
decided it:

- **Only `diff` answers outside a repository.** Run from a directory in none,
  24 of the 25 public reads in `vcs` already declined, every one because at
  least one of its calls exits 128 there. `changed_items` was the only read
  that answered, because both its calls are `diff`s.
- **A revision diff never exits 1 inside one.** Every `diff` shape the module
  issues exits 0, 128 or 129: a bad revision, `A...B` with no merge base, a
  root commit's parent and a pathspec outside the tree all exit 128 (git
  2.43.0). The 1 comes only from the filesystem comparison git runs under the
  same name outside a working tree, which git-diff(1) says "implies
  `--exit-code`".
- **Nothing loses a real 1.** No caller passes `--exit-code` or `--quiet`, and
  `_run_git` returned `""` for a 1 anyway, so a status could never reach one.

The probe route was the weaker one. It adds a process to every read to guard
24 reads that already decline, and it leaves `_run_git`'s table wrong for the
next `diff`. Fixing the classification covers every `diff` in the module:
`_superseded`, `files_in_flight` and `records_on_base` as well as this read.

**The test is in `test_vcs_silence.py`, not `test_vcs.py`.** `test_vcs.py`
says in its module docstring that git is "injected rather than invoked" and
that it tests "the filtering rather than the plumbing", while this defect is in
the plumbing. The sweep is also the file this brief names as blind to it. So
the test is `test_every_read_declines_from_a_directory_in_no_repository`, run
over all of `READS`, so any read added later is held to it too. A second
test, `test_a_diff_outside_a_repository_is_git_not_answering`, pins the new
table row. `verify:` and `touches` were rewritten to match, and the
closing session did that, not a reviewer. Against the pre-fix `vcs.py`
exactly those two fail, on `changed_items` and the classification, and the
other 24 reads pass.

**What is left is not a defect today.** `show <rev>:<path>` also exits 128
outside a repository, and `_asks_for_a_blob` reads that as the file being
absent. No read is made of blob calls alone, so each still declines on another
call, and the sweep fails on the first read that ever is.
