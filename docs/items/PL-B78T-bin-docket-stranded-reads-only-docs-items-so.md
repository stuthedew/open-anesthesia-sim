---
id: PL-B78T
title: bin/docket stranded reads only docs/items, so unmerged work anywhere else is invisible to it: four recovered PR bodies on claude/festive-allen-nj1x98 and 206 lines of docket source on claude/recurrence-signal-feature-3hnynt sit on branches with no open pull request and nothing reports either
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-21
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
