---
id: PL-64LS
title: Detect items stranded on an unmerged branch
priority: P3
effort: S
status: ready
classes: session-cost
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/vcs.py
added: 2026-08-24
---

**Problem.** An item is committed on whatever branch the capturing session was
on. If that branch is never merged, the item exists only there: `docket` reads
`docs/items/` in the current checkout, so no other session's digest or
`docket list` will ever mention it, and the thought is lost as silently as if
it had stayed in the conversation.

**Why it matters.** The queue exists to make capture unloseable. A hole that
only opens on abandoned branches is exactly the hole nobody notices, because
the sessions that could notice are the ones that cannot see the item.

**Where.** `subprojects/docket/src/docket/store.py` (`read_items` reads the
working tree only), `subprojects/docket/src/docket/vcs.py` (already knows how
to ask git about branches).

**First step.** Decide whether detection belongs in the tool or in CI. `vcs.py`
can already run git, so a `docket stranded` command could list item files added
on unmerged branches via `git log --all --diff-filter=A --name-only` and absent
from both the working tree and the default branch.

**Done when.** An item committed on a branch that is closed without merging is
reported somewhere a later session will see it, or the limitation is documented
in `subprojects/docket/README.md` as accepted, with the reason.

**Context.** Carried over from the single-file queue, where it applied to inbox
notes. One file per item did not remove it: the mitigation is still that an
item is committed alone, so recovering one is a single `git cherry-pick`.
