---
id: PL-8MJ3
title: bin/docket triage's 'already edited on a branch' mark reads the merge base, so it keeps firing after that branch's edit has merged - it told one pass to skip four of its five items, every one a false positive
priority: P2
effort: M
status: blocked
blocked-by: PL-R808
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, .claude/skills/docket/SKILL.md
added: 2026-09-07
verify: uv run pytest -q subprojects/docket/tests/test_vcs.py && grep -q 'def test_an_item_file_already_on_the_base_is_not_reported_as_edited_on_a_branch' subprojects/docket/tests/test_vcs.py
---

**Problem.** `bin/docket triage` marks an item `Its file is already edited on
<branch>` from the item files a branch's own commits touched. It does not ask
whether those edits are still only on the branch. After a squash merge the
branch's commits are never on the base — the merge made a new commit — so the
branch stays "ahead" indefinitely and keeps reporting edits the base already
holds.

**Measured 2026-09-07.** A triage pass on the five open captures was told to
skip four of them:

| Item | Reported against | Branch copy vs `origin/main` |
| --- | --- | --- |
| `PL-CZFY` | `origin/claude/gate-items-al6kr2` | identical |
| `PL-H2K2` | `origin/claude/gate-items-al6kr2` | identical |
| `PL-HLD5` | `origin/claude/chart-traces-contrast-59clod` | identical |
| `PL-THXF` | `origin/claude/chart-traces-contrast-59clod` | identical |

Every mark is evidentially wrong: each branch's copy of the item file is
byte-identical to the copy on `origin/main`, both branches having squash-merged
as `#421` and `#422`. There was no unmerged edit on either. Nothing prunes the
refs, because `.claude/hooks/no-prune-guard.sh` correctly refuses `git fetch
--prune`.

**One of the four was nonetheless a real collision, on a branch the mark did
not name.** `PL-HLD5` was picked up on `origin/claude/gate-items-al6kr2` about
an hour later and answered there as `#427`. So skipping it was right, and the
mark's evidence was still wrong: it pointed at
`origin/claude/chart-traces-contrast-59clod`, which held nothing then and holds
nothing now. That is the shape of the defect rather than an exception to it — a
mark that fires on merged history cannot be read as evidence of anything, so a
session cannot tell the one case that mattered from the three that did not, and
in this pass the two were separated only by fetching every ref and diffing each
file by hand.

**Why it matters.** `.claude/skills/docket/SKILL.md` tells a triage pass to obey
this mark: "a second answer here is a second resolution of the same file, so
skip it." Obeyed literally, this pass would have triaged one item of five and
left four untriaged — and would have left them untriaged on every future pass
too, because the stale ref never goes away. That inverts the mark's purpose: it
was added by `PL-N1JK` so a triage pass would not be silently duplicated, and it
now silently suppresses triage instead. It is also the failure mode `CLAUDE.md`
names first — a check that gives a wrong answer while looking authoritative —
and the wrong answer is on the side that loses work rather than the side that
duplicates it.

There is no cheap way for a reader to tell the two cases apart from the output:
"already edited on `origin/claude/foo`" reads the same whether that branch holds
an unmerged answer or merged three days ago.

**Where.** `subprojects/docket/src/docket/vcs.py` already has the machinery this
needs. `_read_refs` (~620-660) walks the candidate branches, resolves each fork
point with `merge-base`, and calls `_landing_split` against `_base_blobs` to
decide via `_work_already_on_base` whether a branch's work is on the base
already. That test is whole-branch: both branches here carry other commits that
genuinely are not on the base, so each is correctly `unlanded`, and the per-item
mark is then computed from every item file the branch touched without consulting
the split. `subprojects/docket/src/docket/render.py:861` is where the line is
emitted (and ~590 the related `QueueEdit` form).

**Done when.** An item file whose blob on the branch is already reachable from
the default branch is not reported as edited on that branch, so the mark fires
only where a genuinely unmerged edit exists; the whole-branch `unlanded` verdict
is unchanged; `subprojects/docket/tests/test_vcs.py` carries
`test_an_item_file_already_on_the_base_is_not_reported_as_edited_on_a_branch`;
and if the mark can still be wrong in the other direction, `SKILL.md`'s
instruction to skip says what to check before obeying it.

**Note.** Do not fix this by pruning refs. A stale `origin/<branch>` can be the
only surviving copy of an item captured on a branch nobody merged, which is what
`bin/docket stranded` recovers and what `PL-HKF4` came within one prune of
losing. The blob is already the right question, and `_base_blobs` already
answers it.

**Blocked on `PL-R808` 2026-09-12**, by the workflow-lane consolidation the
project owner approved. This item is a false positive of the *content*
comparison in `vcs.orphaned` / `_base_blobs`, and `PL-VV4D` has since decided
that the comparison is replaced by an exact `refs/pull/<n>/head` test built in
`tools/`. Working this one now means patching the heuristic that is about to be
replaced - and the cluster it belongs to runs at r = 1.05, generating more work
than it closes, precisely because each such patch lets the next shape through.

It is blocked rather than merged. Its brief carries an observation the others
do not, and the `PL-6ZQY` sweep refuted 56 of 62 proposed merges on exactly
that ground - the surviving brief did not cover what it was said to absorb. So
nothing here is folded into anything; this item simply stops being startable
until the exact check exists.
