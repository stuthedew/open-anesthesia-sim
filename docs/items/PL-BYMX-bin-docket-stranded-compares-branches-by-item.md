---
id: PL-BYMX
title: bin/docket stranded compares branches by item id, so a branch carrying a non-item file the default branch lacks is reported by nothing
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-20
payoff: stops a branch deletion being decided on a check that reports nothing about the files that are not queue items
verify: grep -q 'def test_a_branch_carrying_a_non_item_file' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket stranded compares branches by item id, so a branch carrying a non-item file the default branch lacks is reported by nothing

**Measured 2026-09-20**, while closing `PL-QNQJ`, and it is a fired instance
rather than a hypothetical.

`origin/claude/practical-brown-wr7u6i` carried one commit `main` never took.
Two of its files were item files, which `PL-T2YR` recovered. The third was
18 lines of `ROADMAP.md` - the paragraph recording why `PL-ZM48` was declined
to Gate 2 - and no command this project runs ever mentioned it. Both halves
of `stranded` are keyed on items: `stranded()` builds `on_base` from
`_items_at()` and reports ids the base's tree lacks, and `_carried_work()`
takes an `item_path` per item and additionally needs the branch's own pull
request to have merged, which this branch never had. A file that is not an
item is outside both readings.

**The window closed while the recovery was being written.** The ref stood
when this session read it and was gone about twenty minutes later, deleted by
the project owner - correctly, on `PL-66Z5`'s finding that the superseded refs
carry nothing `main` lacks. The paragraph survived only because the session had
already copied it into a working tree; on the remote it was gone, and one
container's stale `refs/remotes/` entry is what it had been reduced to. That is
the hazard `CLAUDE.md` names in "an uncommitted thought is one interruption
from gone", with the prune replaced by a legitimate deletion, taken on a check
that could not see the file.

**Why it matters.** The deletion decision is made on `stranded`'s answer -
`PL-66Z5` compared every superseded ref file-by-file precisely because nothing
reported them, and the eleventh ref was excluded from that pass by being the
pass's own branch. So the one ref that no file-by-file comparison covered is
the one that carried an uncovered file. A check that says "no branch carries
work the default branch lacks" while a branch carries a paragraph of the
roadmap is giving a wrong answer silently, which is the first of `CLAUDE.md`'s
three compounding-friction tests.

**Done when.** Decide what a non-item comparison can assert without becoming
noise - every live branch legitimately differs from `main` in files it is
mid-way through changing, so the naive version reports every session - and
either extend `stranded` to it or record why the item-keyed reading is the
only one that can be trusted. `PL-W7H9` states the general form of what a
branch comparison may assert; this is the case it does not reach.

**The `PL-W7H9` reference above is wrong, and is corrected here rather than
deleted** (triage, 2026-09-20). `PL-W7H9` is "State what a branch comparison
asserts and what it does not, in docs/MODEL.md and docs/ARCHITECTURE.md" -
`classes: docs, safety, anticipated`, `feature: scenario-branching`, its own
`blocked-by` then naming `PL-8PSW` and `PL-VKJW`. Its "branch" is a *simulation
scenario branch*: two runs forked at an instant and drawn side by side, where
the hazard is a reader taking "low flow woke this patient 12 minutes sooner" as
a result about patients. It states nothing about git branches and nothing this
item can build on, so there is no general form waiting upstream and no blocker
here. The two items share a word.

**So the design question is this item's own, and it is the whole of it.** Every
live branch legitimately differs from `main` in the files it is mid-way through
changing, so a naive non-item comparison reports every running session - which
is the check `CLAUDE.md` retires for firing every run without changing a
decision. What `stranded` can assert about a *non-item* file has to be narrowed
by something: a merged pull request whose branch kept a later commit, a ref
whose session is gone, an age threshold, or nothing at all. Deciding that is
the work.

**The instance is closed and cannot be re-run, which sets what evidence is
available.** `origin/claude/practical-brown-wr7u6i` was deleted on 2026-09-20,
correctly, and `PL-QNQJ`, `PL-T2YR` and `PL-66Z5` are all `done`. So a fix is
designed against the shape rather than reproduced against the ref, and the
reproduction in the paragraphs above is the record of it.

**Re-pointed at `tools/left_behind_check.py`, 2026-10-11 (`PL-2C53`): that
check answers none of this.** It reads every branch on `origin`, but before
comparing anything it clears one with no pull request ("no pull request was
opened from it"), one whose pull request is open, and one whose pull request
closed unmerged. It answers only for a branch whose newest pull request merged.
`claude/practical-brown-wr7u6i` never had a pull request, so the design
question above stands whole.

**`PL-B78T` was dropped into this item the same day**, as a later filing of the
same hole. It asked for a branch "with no pull request open on it and none
merged from it", holding content the default branch lacks, to be named by
`stranded` with the command that would recover it. Its two instances were
settled elsewhere, so what it adds here is one shape: a pull request closed
unmerged leaves its branch in this hole as surely as none does. If the design
extends `stranded`, a recovery command beside each name comes with it.

**What changed the stakes since filing.** `tools/branch_sweep.py` (`PL-X8SV`)
now deletes finished `claude/` branches daily, and copies each tip to
`refs/archive/<branch>/<tip>` in the same push. It keeps a branch while a pull
request is open on it, a claim holds unfinished work on it, `stranded`,
`orphaned` or the exact check reports it, or its last commit is under 72 hours
old. This item's shape, once those 72 hours pass, holds none of them, so it is
archived with nothing having named the file. The work is no longer lost when
the ref goes. It moves to a ref no default fetch reads, named only in the
sweep's run log. The design question above should weigh that: answering
"nothing at all" now costs a restore from an archive nobody is told about, not
the work itself.
