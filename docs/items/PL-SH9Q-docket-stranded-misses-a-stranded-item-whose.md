---
id: PL-SH9Q
title: docket stranded misses a stranded item whose file already exists on the base, because it reads branch-only adds rather than branch-only content
status: untriaged
added: 2026-09-16
---

**Problem.** `bin/docket stranded` reports an item as existing "only on a
branch" when the *file* is absent from the default branch. An item whose file
is already on the base and which a branch has **modified** is invisible to it,
however much of the item's substance lives only on that branch.

**The instance.** `origin/claude/wizardly-maxwell-dyzpjt` carried two commits,
both queue-only:

- `PL-WXX8` — a new file, correctly reported as stranded.
- `PL-PX7V` — an existing file taken from `untriaged` to `done`, gaining a
  `verify:`, a `closed:` date and a 55-line recorded result: `/doctor`'s
  CLAUDE.md trim check run against all eleven checked-in instruction files,
  returning zero cuts, plus the one candidate it examined and rejected.
  **Not reported.**

So the command named the 52-line capture and missed the 60-line closure of a
finished item. The session holding that branch was archived, so the only thing
standing between that result and its being lost was somebody reading the branch
by hand.

**Why it matters.** The command's whole job is "what would be lost if this ref
went away", and the answer it gives is narrower than the question in a way the
reader cannot see. A closure is the *most* expensive kind of stranding: the work
is finished, so nobody will redo it deliberately - a later session re-derives it
from scratch instead, which for `PL-PX7V` means re-running the whole trim check
against eleven files to learn again that it returns nothing.

It is also the shape the apparatus floor names: `.claude/rules/apparatus-standard.md`
requires that what this apparatus tells a session be true or say what it could
not read. "25 items exist only on a branch" reads as a complete answer and is
not one.

**Found 2026-09-16** while recovering that branch under `#631`, after
`bin/docket stranded` had reported it as holding one item.

**Where.** Whichever function in `subprojects/docket/src/docket/` backs
`stranded` - it compares the branch's item filenames against the base's;
`subprojects/docket/tests/`.

**Shape, not a decision.** The fix is to compare item *content* rather than
filename presence, but what counts as a stranded modification needs deciding:
every branch that touches any item file would otherwise be reported, including
the ordinary case of a live branch editing its own item, which would make the
command fire constantly and be routed around. A narrower rule worth costing
first: report a modification that **closes** an item - `status` moving into
`done` or `dropped` on a branch the base has not taken - since that is the case
where the work is finished and nobody will repeat it. Whether to report other
modifications at all is the open question.

**Done when.** `bin/docket stranded` names an item whose file exists on the base
but whose closure exists only on a branch, or states in its own output that it
reports branch-only files and not branch-only content. A test in
`subprojects/docket/tests/` pins it against exactly the
`wizardly-maxwell-dyzpjt` shape: one added item file and one existing item file
closed on the branch.
