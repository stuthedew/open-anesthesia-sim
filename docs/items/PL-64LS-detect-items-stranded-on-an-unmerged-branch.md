---
id: PL-64LS
title: Detect items stranded on an unmerged branch
priority: P2
effort: S
status: done
classes: session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, .claude/hooks/docket-digest.sh
added: 2026-08-24
verify: uv run pytest subprojects/docket/tests/test_vcs.py subprojects/docket/tests/test_cli.py
closed: 2026-08-31
pr: 108
commit: 97ed318
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

**Decided (2026-08-31).** In the tool, not in CI, and surfaced through the
session digest. The requirement is that *a later session* sees it, and CI
reports to whoever reads the run - so a CI job would answer the question in a
place the reader who needs it never looks. `docket stranded` prints the full
report; the digest carries one line, and only when there is something to say.

**Built by content, not by commit counts.** The sketch above (`git log --all
--diff-filter=A`) was replaced with a per-ref `git ls-tree` compared by item
id. Three reasons, each of which would have made the sketch report items that
are not lost: a squash-merged branch contains none of its own commits, so it
reads as unmerged forever; a renamed item file was added twice and deleted
once, so its old name reads as added-and-gone; and an agent session's
container is a shallow clone, where every commit-graph question - containment
included - is unreliable. `ls-tree` reads one tree and needs no history behind
it.

**The enabling half was the fetch.** A session container clones one branch, so
before this the checkout held two refs and the check could only ever have
answered "nothing stranded". `.claude/hooks/docket-digest.sh` now fetches every
branch tip rather than `main` alone - measured at well under a second - and
deliberately does not prune, since a tracking ref for a branch deleted on the
remote may be the only copy of what was committed on it.

**Closed (2026-08-31).** `docket stranded` found one on its first run:
`PL-D2GW` existed only on `claude/roadmap-release-write-failure-nhsjwo`,
whose pull request 101 had merged the day before a later session pushed one
more capture commit to it. Recovered in the same branch with the `git
checkout` line the report prints.
