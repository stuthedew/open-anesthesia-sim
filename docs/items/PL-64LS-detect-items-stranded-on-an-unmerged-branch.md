---
id: PL-64LS
title: Detect items stranded on an unmerged branch
priority: P2
effort: S
status: ready
classes: session-cost
feature: dev-tooling
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

**Promoted from P3 (2026-08-25).** The hole stopped being hypothetical twice
in one session. Cleaning up branches after the debt-gate merges needed a manual
investigation of every remote branch to answer "is it safe to delete this?",
and the answer turned on content rather than on git's commit counts:
`codex/batch-pl-qgzv-...` showed seven unmerged commits that were entirely
obsolete, while `claude/public-private-repo-strategy-3bc16d` showed one that
carried the only copies of PL-Y2GG and PL-Z4GF. Deleting on the commit count
would have been wrong in both directions. Separately, `docket flight` was
reporting PL-QGZV as in-flight on a branch whose work had long since landed.

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
