---
id: PL-5QLP
title: bin/docket record renames an item file whose name predates its current title while writing pr:, so the write two sessions are told git will merge is a delete-plus-add, and reverting it with git checkout leaves a duplicate-id error
priority: P2
effort: S
status: done
classes: defect, infra
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/store.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'restores the tracked deletion' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket record renames an item file whose name predates its current title while writing pr:, so the write two sessions are told git will merge is a delete-plus-add, and reverting it with git checkout leaves a duplicate-id error

**Observed 2026-09-19 on `origin/main` at `11125d9`.** A bare `bin/docket
record` wrote `pr:` for sixteen items owed one. Fifteen came back as ordinary
modifications; `PL-XQRK` came back as a delete plus an untracked add -
`docs/items/PL-XQRK-a-session-cannot-delete-a-remote-branch-git.md` removed and
`...-branch-so.md` created. The file's name on the base was derived from an
older title; the current one ends "without saying so up front", so re-deriving
the name while writing the field renamed the file.

**Why that matters more than a tidier filename.** The `docket` skill grants
`record` a standing exemption from the in-flight guard every other item-editing
path owes, and the reason it gives is that "two sessions that both run it write
the same tool-dictated line and git merges them". A single added line does
merge. A rename does not: two branches that both run `record` against the same
stale name produce a delete-plus-add each, and the second to merge takes a
modify/delete conflict on a file nobody edited on purpose. The exemption's own
justification does not cover the behaviour.

**And the revert is a trap.** `git checkout -- docs/items/` restores the
tracked deletion and leaves the untracked new name, so the store then holds two
files for one id and `bin/docket check` errors with `PL-XQRK: used by more than
one file`. A session that runs `record` with no commit to ride - which the
skill tells it to do, since the write is meant to ride a commit it is already
making - and then backs the write out reaches a broken store by following the
instructions. `git clean -f docs/items/` is what actually finishes the revert,
and nothing says so.

**Where.** `bin/docket record` in `subprojects/docket/src/docket/cli.py`, the
filename derivation in `subprojects/docket/src/docket/store.py`, and the
`record` paragraph under **Mode: close out an item** in
`.claude/skills/docket/SKILL.md`.

**Not urgent, and this is why.** It is loud rather than silent: the duplicate
reaches `bin/docket check` as an error, not a wrong answer that passes. It does
not sit upstream of every command - `record` runs from `make fix` and the
close-out, not from `next` or the digest. And nothing routes around it today.
So it is an ordinary capture rather than a compounding-friction interruption.

**Done when.** Either `record` writes the field without re-deriving the
filename - leaving a rename to whatever command changes a title - or the skill
stops telling sessions the write is one git can merge, and says what finishes a
revert. Which of the two is a decision: a filename that has drifted from its
title is a real inconsistency, and this is about whether the field write is the
right moment to repair it.

**Answered 2026-09-19, and both endings taken.** The question this item posed -
whether the field write is the right moment to repair a drifted filename - was
already settled in the tree: `store.rewrite_item`, added by `PL-L4YG`, exists
precisely so a field write keeps its name, and leaves renaming to a pass of its
own (`PL-YTDN`). So the answer is the first of the two this brief offered, and
it was not a fresh decision: `record` and `release` were simply never wired to
a helper built for them.

The second ending is discharged by the first rather than separately. Once no
field write renames, `record` writes one added line, which is the merge the
`docket` skill's standing in-flight exemption promises - so that paragraph
became true instead of needing correction. And `git checkout -- docs/items/`
now reverts completely, because there is no untracked new name left behind for
`bin/docket check` to report as one id used by two files. Verified on the real
store: a bare `bin/docket record` wrote 25 owed numbers as 25 modifications
with no delete and no untracked add, and the checkout restored the tree to
clean.

**This item is a re-discovery of `PL-LBR6`**, filed 2026-09-13 with the same
diagnosis and a `verify:` command already written. It is closed rather than
dropped because it was not only a duplicate: the revert trap is its own
finding, `PL-LBR6` never recorded it, and `PL-QMC0` was blocked on reading
this file. Its `verify:` pins the sentence in the regression test's docstring
that carries that finding.
