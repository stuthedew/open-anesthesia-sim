---
id: PL-B78T
title: bin/docket stranded reads only docs/items, so unmerged work anywhere else is invisible to it: four recovered PR bodies on claude/festive-allen-nj1x98 and 206 lines of docket source on claude/recurrence-signal-feature-3hnynt sit on branches with no open pull request and nothing reports either
priority: P2
effort: M
status: dropped
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-21
closed: 2026-10-11
reason: Duplicate of PL-BYMX for what is left, and its two instances were settled elsewhere: festive-allen's bodies reached main, and recurrence-signal's commit sat past the head #793 merged, which tools/left_behind_check.py reported on its first run and #794 held (PL-SRBR). A branch with no pull request holding content main lacks is PL-BYMX's question, which also records the noise this Done-when would have reported.
payoff: work pushed to a branch that never had a pull request is named before the container holding it is reclaimed, instead of being findable only by remembering the branch name
verify: grep -q 'def test_a_branch_with_no_pull_request_is_read_for_orphaned_work' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket stranded reads only docs/items, so unmerged work anywhere else is invisible to it: four recovered PR bodies on claude/festive-allen-nj1x98 and 206 lines of docket source on claude/recurrence-signal-feature-3hnynt sit on branches with no open pull request and nothing reports either

**Re-measured 2026-09-21** on a fresh checkout of `main`. `bin/docket stranded`
closed with a line saying no branch carries work its own pull request left
behind, across the 16 unmerged branch refs it read, while
`origin/claude/recurrence-signal-feature-3hnynt` still exists on the remote and
carries docket source `main` does not hold. The other branch named above,
`claude/festive-allen-nj1x98`, is gone from the remote and its four recovered
bodies are on `main` under `docs/pr-bodies/`, so that half of the original
observation resolved itself and is no longer evidence.

**Why it matters.** The item half of `stranded` reports ids, so a branch whose
work is a script, a rule file, a recovered pull request body or a test carries
nothing it can name and is read as empty. The `orphaned` half exists for that
and is scoped to branches whose own pull request merged without them, which is
`PL-CZR6`'s subject; a branch that never had a pull request at all falls outside
both. The miss is silent and permanent - nothing says the read was partial - and
the container is ephemeral, so the only thing standing between the project and
losing that work is a session remembering the branch name.

**Done when.** A branch holding content the default branch does not, with no
pull request open on it and none merged from it, is named by `bin/docket
stranded` together with the command that would recover it; and a test in
`subprojects/docket/tests/test_vcs.py` drives that shape.

**Dropped 2026-10-11 (`PL-2C53`), as `PL-BYMX`'s duplicate for what is left.**
Both instances in the title are settled. `claude/festive-allen-nj1x98`'s four
bodies reached `main`, as the paragraph above records. And
`claude/recurrence-signal-feature-3hnynt` was not a branch without a pull
request: `#793` had merged from it, and its one commit pushed afterwards,
`52c6d698`, is what `tools/left_behind_check.py` reported on its first run.
`#794` held every line of it, and the branch was deleted (`PL-SRBR`). What the
Done-when asks for is a branch with no pull request open and none merged that
holds content the default branch lacks. That is `PL-BYMX`'s question, filed a
day earlier, and that item also records what this Done-when would have walked
into: every live session's branch holds such content, so the naive comparison
reports them all. The exact check does not reach the shape, since it clears a
branch with no pull request, and one whose pull request closed unmerged, before
comparing anything. `PL-BYMX` now carries both shapes and this item's place in
`stranded-report-fidelity`.
