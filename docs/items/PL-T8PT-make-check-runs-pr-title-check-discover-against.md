---
id: PL-T8PT
title: make check runs pr_title_check --discover against committed history, so a session that runs it before committing the closure sees a HEAD without it, passes locally, and goes red in CI anyway
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: tools/pr_title_check.py, tests/unit/test_pr_title_check.py, Makefile
added: 2026-09-12
---

**Problem.** make check runs pr_title_check --discover against committed history, so a session that runs it before committing the closure sees a HEAD without it, passes locally, and goes red in CI anyway

**Observed 2026-09-12** on `#499`, and it is a *residual* of `PL-J3BB`
(`make check` cannot run `pr_title_check.py`), which is `done` and shipped in
v0.4.3. That item closed the "nothing locally can catch it" half by adding
`--discover`. This is the half left behind.

**The sequence, because the sequence is the finding.** The session dropped five
items and closed a sixth, then:

1. ran `make check` - green, `pr_title_check.py --discover` included;
2. `git commit`;
3. `git push`;
4. CI ran `pr-title` and failed, naming all five dropped ids the title lacked.

Nothing went wrong in either the tool or the run. `closes()` compares
`origin/main...HEAD`, so at step 1 the closures were still unstaged working-tree
edits and `HEAD` genuinely did not close them. The check answered correctly
about the tree it was shown, and the tree it was shown was one commit short of
the one that would be pushed.

**Why this is not `PL-J3BB` again.** That item's failure was "the gate does not
exist locally". This one's is "the gate exists locally and is consulted at the
wrong moment" - `make check` is run *before* committing, which is the whole
point of a pre-commit gate, and this is the one check in the suite whose input
only becomes true *after* the commit. `dropped` counts here exactly as `done`
does, which is what made five ids appear at once.

**Approaches, none chosen:**

- Have `--discover` read the index and working tree as well as `HEAD`, so it
  answers about the tree that is *about to* be committed. Closest to correct,
  and it makes the check answer a different question from the CI one.
- Move the check to a pre-push hook, where `HEAD` is final. Right moment, but
  it leaves `make check` still able to pass on a title that will fail.
- Have it print the ids a title must lead with rather than pass or fail
  locally - the third approach `PL-3BC5` contributed to `PL-J3BB` and which
  was not the one built.

**Not delegable as filed:** which of the three is right is an open question.

**Why it matters.** `CLAUDE.md` names an advisory being routed around as one of
the three findings worth interrupting for, and this is the shape one step
earlier: a gate that passes locally and fails in CI on the same tree teaches a
session that running it before committing is pointless. `make check` is the
project's pre-commit gate and every other check in it answers about the working
tree; this one answers about `HEAD`, which at that moment is always one commit
short of what will be pushed. The cost is a full CI round trip per closure, and
it lands on exactly the sessions doing the right thing - the ones that close
items in the same commit as the work, as the close-out procedure requires.

`dropped` counts here as `done` does, which is what made five ids appear at once
on `#499`: a triage pass that drops five items and closes a sixth fails
`pr-title` on all six.

**Decision needed.** Which of the three approaches is taken, and it is a genuine
three-way rather than an obvious first choice:

1. **`--discover` reads the index and working tree as well as `HEAD`**, so it
   answers about the tree that is about to be committed. Closest to correct for
   the local moment, and it makes the local check answer a different question
   from the CI one, which is its own hazard.
2. **Move the check to a pre-push hook**, where `HEAD` is final. Right moment,
   but it leaves `make check` still able to pass on a title that will fail, so
   the misleading green stays.
3. **Print the ids a title must lead with, rather than passing or failing
   locally.** The third approach `PL-3BC5` contributed to `PL-J3BB` and which was
   not the one built - it removes the false green by removing the verdict.

**Done when.** One approach is chosen with its reasoning recorded, built, and a
session that closes an item in the same commit as its work either sees the
failure before pushing or is told plainly that the local run cannot answer.
