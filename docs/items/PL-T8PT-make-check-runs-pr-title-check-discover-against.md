---
id: PL-T8PT
title: make check runs pr_title_check --discover against committed history, so a session that runs it before committing the closure sees a HEAD without it, passes locally, and goes red in CI anyway
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/pr_title_check.py, tools/pr_record_check.py, tests/unit/test_pr_title_check.py, tests/unit/test_pr_record_check.py, Makefile, .claude/skills/docket/modes/close-out.md
added: 2026-09-12
verify: grep -q 'def test_a_closure_written_but_not_committed_is_refused_before_the_commit' tests/unit/test_pr_title_check.py
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

[superseded 2026-09-27: approach 1 chosen, § "Answers 2026-09-27"]
**Approaches, none chosen:**

- Have `--discover` read the index and working tree as well as `HEAD`, so it
  answers about the tree that is *about to* be committed. Closest to correct,
  and it makes the check answer a different question from the CI one.
- Move the check to a pre-push hook, where `HEAD` is final. Right moment, but
  it leaves `make check` still able to pass on a title that will fail.
- Have it print the ids a title must lead with rather than pass or fail
  locally - the third approach `PL-3BC5` contributed to `PL-J3BB` and which
  was not the one built.

[superseded 2026-09-27: answered, § "Answers 2026-09-27"] **Not delegable as
filed:** which of the three is right is an open question.

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

## Design round 2026-09-27: recommendations

**Re-confirmed against the tree, 2026-09-27.** `closes(base, head)` in
`tools/pr_title_check.py` still subtracts `closed_items_at(base)` from
`closed_items_at(head)`, each read with `git ls-tree` and `git show
ref:path`, and under `--discover` `head` defaults to `HEAD`. So a
`status: done` or `dropped` still in the working tree is invisible to `make
check`, and `pr-title.yml` fails on the same tree one push later. Of the
commits this shallow clone holds, only `PL-MT3R`'s remote-listing change has
touched the script since filing. Two things around it have changed.

**What changed since filing.** First, `PL-HMZZ` moved provenance off the
subject: `bin/docket record N` writes `pr:` onto each closure before the
merge and `tools/pr_record_check.py` refuses the pull request until it does,
so a stale title now costs a `git log` reader a line and nothing else - but
`pr-title` has been a required check since 2026-09-17 (`PL-H8YD`), so a miss
still costs a CI round trip and a red run beside a green one (`PL-X1S4`).
Second, and the finding that decides the approach: `record N` already reads
the set this item wants. `cli.cmd_record` writes onto "every closure this
checkout introduces - `done` here and not on the default base, committed or
still in the working tree", which `_record_on_branch` calls "the two moments
`make check` runs at", through `vcs.changed_items` and
`vcs.closures_on_base`; and `cmd_record`'s docstring calls that "the set
`tools/pr_title_check.py` holds the title to". It is not: the title check
reads `HEAD`. So docket's own writer and the title check disagree at exactly
the pre-commit moment, and `pr_record_check.py`, which imports
`closed_items_at`, inherits the blind spot and says so in its docstring ("a
closure still in the working tree is not seen until it is committed"). The
close-out mode papers over both with a rule - "retitle an open pull request
to lead with the same ids, and do it before pushing the closure ... a session
knows what its commit closes before it pushes" - which is the
advisory-being-routed-around shape `CLAUDE.md` names as worth fixing.

**Q1. Which of the three approaches?** **Recommendation: approach 1, narrowed
to the local run - under `--discover`, the head side reads the working
tree.** `make check` then answers about the tree that is about to be
committed, which is the question a pre-commit gate is for, and it is the same
set `record N` writes onto, so the two stop disagreeing by construction. CI is
untouched: `pr-title.yml` sets `PR_TITLE` and `PR_BASE`, never `--discover`,
and reads the pushed head as it does now. `pr_record_check.py --discover`
inherits the read through the shared `closed_items_at`, and that is right
rather than incidental: `record N` writes `pr:` into the working tree before
the closure commit, so the record half confirms it at the same moment instead
of one commit later, and the `Makefile`'s "a closure counts once committed"
retires with it.

*The hazard the brief names - the local check answers a different question
from CI's - is real, and is paid in one word.* A working-tree closure the
session never commits is reported locally and never reaches CI. That is a
true statement about the checkout rather than a wrong one, and the failure
line says where it read: "this checkout closes PL-XXXX (working tree)". A
session that meets it has a closure to commit or a stray edit to look at,
and both are worth the line. A working tree that cannot be read - no
`docs/items` on disk - declines rather than reads as empty, as `PL-1PBV`
requires of the ref reads.

*Refused: a pre-push hook.* Nothing in the tree installs git hooks and this
checkout's `core.hooksPath` is unset; the repository's hooks are Claude Code
`PreToolUse` hooks in `.claude/settings.json`, so the realistic form is a
Bash-matcher hook that runs the check when the command is a `git push`. It
reads a final `HEAD`, and it leaves `make check` green on a title that will
fail - the brief's own objection - pays a network lookup inside a hook on
every push, never fires for a push from a terminal or the Mac, and is a new
workflow mechanism where a small change to an existing check answers.

*Refused: print the ids and give no verdict.* The failure path already prints
the exact remedy ("Rename the pull request to lead with the ids ..."), and a
branch with no pull request open is a silent skip by design; printing on
every branch that closes anything, right title or wrong, is a line that fires
every run without changing a decision, which `CLAUDE.md` retires.

*Considered and set aside: make the working tree the default head everywhere,
whenever neither `--head` nor `PR_HEAD` names a ref.* One rule and no mode,
and CI's answer would not change, since a fresh checkout's working tree is
its `HEAD`. Set aside because it changes CI's read path for no change in
answer; `--discover` already marks the local run and is the narrower edit.

**How, for the build thread.** In `tools/pr_title_check.py`, a working-tree
reader beside `closed_items_at`: list `docs/items/*.md` on disk, `parse_item`
each, keep `CLOSED_STATUSES` - standard library only, and cheaper than the
`git show` per file the `HEAD` read costs. Under `--discover` with no
explicit `--head`, `closes()` takes the working tree as its head; an explicit
`--head REF` keeps reading the ref, so the existing tests and `pr-title.yml`
are unchanged. Name the source in the failure line. Tests in
`tests/unit/test_pr_title_check.py`: a closure on disk and absent at `HEAD`
is refused under `--discover`; an explicit `--head` still reads the ref; a
closure at `HEAD` and reverted on disk is not this branch's; and
`tests/unit/test_pr_record_check.py` for the record half's inherited read.
Four sentences of documentation move with it: the `--discover` paragraph of
`pr_title_check.py`'s docstring, the "reads the committed tree" sentence of
`pr_record_check.py`'s, the `Makefile` comment above the record line, and
`.claude/skills/docket/modes/close-out.md`'s "`make check` then reads the
committed tree". `touches:` gains `tools/pr_record_check.py`,
`tests/unit/test_pr_record_check.py` and `modes/close-out.md`; `S` holds.

**Done when, restated for the choice.** A session that closes an item and
runs `make check` before committing sees the title failure then, with the
working tree named as what was read; CI's verdict on the pushed head is
unchanged; and `record N`, the title check and the record check agree on
what this checkout closes.

## Answers 2026-09-27

**Answered 2026-09-27: approach 1, narrowed to the local run, ratified**
(project owner, 2026-09-27, ratified, over a pre-push hook and over printing
the ids with no verdict). Under `--discover` the head side reads the working
tree and CI is unchanged, as § "Design round 2026-09-27: recommendations"
specifies. The approach is chosen, so the "not delegable as filed" reason
above has ended and the item is ordinary `S` work; the thread that builds it
sets its status and `touches:`.
