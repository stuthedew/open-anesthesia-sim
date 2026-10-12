---
id: PL-BYMX
title: bin/docket stranded compares branches by item id, so a branch carrying a non-item file the default branch lacks is reported by nothing
priority: P2
effort: M
status: done
classes: defect
feature: stranded-report-fidelity
milestone: v0.5.23
touches: docs/items
added: 2026-09-20
closed: 2026-10-11
pr: 1403
payoff: stops a branch deletion being decided on a check that reports nothing about the files that are not queue items
verify: grep -qF 'Decided 2026-10-11, by this session: nothing at all' docs/items/PL-BYMX-bin-docket-stranded-compares-branches-by-item.md
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

## Design round, 2026-10-11

**Decided 2026-10-11, by this session: nothing at all.** `bin/docket stranded`
keeps the item-keyed reading as the only one it makes about a branch no pull
request merged, and is not extended to that branch's files outside the queue.
Apparatus-internal, and settled by a measurement and by rules this repository
already states, so it is decided in the round rather than put to the owner
(`.claude/skills/docket/modes/design.md`, step 4).

**Re-confirmed against the tree first: the hole stands as filed.**
`_carried_work()` is gone by that name. The half of `cmd_stranded` that reads
files outside the queue is `vcs.orphaned`, which names a branch only where the
base took one of its commits whole (`_commits_by_landing`), so a branch no pull
request merged is outside it, and the item half reads ids.

**Every narrowing that is not noise comes down to the sweep's own rule.** The
four this brief names, each read through the records this project keeps:

| Narrowing | What it asserts | Verdict |
| --- | --- | --- |
| None | every branch holding a file the base lacks, which is every branch being worked | noise: it fires every run without changing a decision, which `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" retires a check for |
| A merged pull request whose branch kept a later commit | already built over every path: `vcs.orphaned` by content, `tools/left_behind_check.py` exactly | the complement of this item's shape, not a narrowing of it |
| A ref whose session is gone | git records no liveness and `docket` cannot ask the harness (`PL-SK88`); the record nearest it is the claim lease, and read through that record it is "no unfinished work and no open pull request" (`claims.unfinished_work`), which is `tools/branch_sweep.py`'s rule | the set the sweep archives |
| An age threshold | an age standing in for liveness, which `.claude/rules/apparatus-standard.md` § "Read the fact from its record" refuses; joined to the row above it is the sweep's 72-hour grace | the same set, in the hours before the sweep archives it |

So the one thing a comparison of a branch's other files can assert without
naming live work is "the sweep will archive this branch, and it carries files
the base lacks". The sweep then archives it.

**Measured, that assertion would have fired once, on a superseded draft.** The
sweep's 16 runs, 2026-09-26 to 2026-10-11, read 28 distinct `claude/`
branches. 27 were held at every reading by an open pull request or by
unfinished work in the claim record, so whatever they carried outside the queue
was work being written. The 28th,
`claude/gifted-pasteur-iwimhy`, was held by the grace alone for three runs and
archived on 2026-10-04 as
`refs/archive/claude/gifted-pasteur-iwimhy/f7978f9ecfdbdd813118984e19fd318b04d63999`,
the only archive ref on `origin`. Its one commit, `f7978f9e`, carries the
subject and the author time (2026-09-30 23:25:37 UTC) of `c5eae102` on `#1250`'s
head, with a different patch id and 529 lines added against `c5eae102`'s 604:
an earlier version of the commit `#1250` landed as `386f0ab1` (inferred: git
keeps the author date through an amend). `vcs.change_landed` answers None for
it, because the later version rewrote the hunks it would replay, so no tool
could have cleared it, and a reader would have had to compare it with `#1250` by
hand. A line naming it would have stood in every reply's refresh
(`.claude/rules/instruction-writing.md` rule 14 runs `bin/docket stranded`
before every closing block) for nine hours with the age threshold, and for
three days and nine hours without it.

**`PL-B78T`'s shape, a pull request closed unmerged, has cost this project
nothing outside the queue, and one paragraph inside it.** 10 of the 1,306 pull
requests with a head ref closed unmerged (the list in `PL-99YZ`'s count, from
GitHub on 2026-10-11). `#59`, `#60` and `#149` predate the history rewrite and
their heads carry pre-rewrite `main`, so they cannot be read against today's.
Of the other seven, four (`#587`, `#1045`, `#1092`, `#1101`) wrote only queue
records, which are the item-keyed reading's to judge: item files, and for
`#1092` and `#1101` the `docs/pr-bodies/` record of their own body, which a pull
request that never merged leaves nothing on `main` to describe. Every line they
add to an item is on `main`, is said there in other words (`#586` landed
`#587`'s drop of `PL-0QLX`), or is a field `main`'s later copy has moved past,
except one paragraph: the measurement `#1092` appended to `PL-X3NY`, still
`ready`, which `#1110` did not carry when it landed `PL-P99G`'s record. Its
branch, `claude/cleanup-unused-branches-bcecxv`, was already gone when the sweep
first ran (2026-09-26 20:21 UTC, ten `claude/` branches read), so it was deleted
by hand (inferred), and `refs/pull/1092/head` held the only copy. The sweep
could not have taken it, since it keeps a branch for "an edit to" an open item
"that main lacks" (its first run's own wording). This round restores the
paragraph to `PL-X3NY`. Three carry a commit outside the queue that
`vcs.change_landed` says never landed, and none is lost work: `#791`'s
near-duplicate print for `PL-TZ7T` shipped through `#793`; `#1127`'s
gate-status-guard change belongs to `PL-QMN0`, which `#1138` dropped; and `#392`
is the project owner's own README change, from `stuthedew-patch-1` rather than a
`claude/` branch, closed 35 seconds after it opened. The paragraph this item was
filed on survived too: `ROADMAP.md` holds it, under "`PL-ZM48`, added
2026-09-20, after the freeze and declined with it."

**Why the item-keyed reading is the only one this check can trust.** An item id
names a unit the store writes, so "the base holds no file for this id" is a
fact a tree answers. A file outside the queue has no such unit, and whether the
base already holds a branch's change once amends, ports and drops intervene is
the fact generator head `PL-R808`'s family misreads: "Whether the base already
holds or has superseded a branch commit's change, by whatever route". The
decidable part is answered already, exactly, by `vcs.change_landed`, and
`claude/gifted-pasteur-iwimhy` shows its answer on the one branch this
comparison would have named: None, for a change that landed in another form.
Nor does anything `stranded` prints claim more than it read. Its item half
names items, and since `#1401` its left-behind half says it judged "work its own
pull request left behind" by file content, so no all-clear covers a never-merged
branch's other files.

**What "nothing at all" costs, now that the sweep archives.** On the sweep's
path, nothing: `tools/branch_sweep.py` copies a branch's tip to `refs/archive/`
in the push that deletes it, its log prints the restore beside the branch, and
`docs/maintainer.md` § "Sweep branches now, or restore one the sweep deleted"
gives the restore and the listing for when the log has expired. So this item's
payoff, no branch deletion decided on a check blind to the files outside the
queue, is bought on that path by the archive rather than by a report. **One
deletion path keeps no copy**: the bare `git push origin --delete` that
`.claude/skills/docket/modes/capture.md` hands the owner for a branch the sweep
keeps that should go anyway, which has run once since the sweep started
(`claude/project-thread-qt3onr`, gone before the 2026-10-04 run with no archive
copy). That is `PL-Y3GK`, filed in this round as the residual of this decision
rather than its build: it makes the hand deletion keep a copy too, which a
report beside the branch could not, since judging what such a branch carries is
the reader's either way.

**What would reopen it.** A branch, archived or deleted by hand, found after the
fact to have carried work outside the queue that never landed in any form; or
the sweep archiving such branches often enough that a restore from an archive
nobody reads stops being rare. Either is filed with `bin/docket new`, naming
this item.

**`touches:` moves to `docs/items`**, since this round changes only item files
and no build follows it. `PL-NPWP`, link 2 of the stranded-report-fidelity
chain, keeps `vcs.py` and `test_vcs.py` to itself, and the chain ends at it.

**Done when** is met by the decision above: the item-keyed reading is recorded
as the only one `stranded` can trust for a branch no pull request merged, with
why.
