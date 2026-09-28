---
id: PL-S17R
title: CLAUDE.md's merge bullet says a session merges only by arming auto-merge and omits docs/maintainer.md's exception for a pull request already clean, where the Squash and merge is the owner's, while the GitHub tool's refusal says 'you can merge directly' - so a session told 'Merge' merged #1224 through the API against PL-V2X5's ratified decision
status: untriaged
added: 2026-09-28
---

**Problem.** CLAUDE.md's merge bullet says a session merges only by arming auto-merge and omits docs/maintainer.md's exception for a pull request already clean, where the Squash and merge is the owner's, while the GitHub tool's refusal says 'you can merge directly' - so a session told 'Merge' merged #1224 through the API against PL-V2X5's ratified decision

**Evidence, 2026-09-28.** The owner answered "Merge" on `#1224` (`PL-4NZ7`),
green on a head current with `main`. `enable_pr_auto_merge` refused: "The pull
request is already in clean status (all checks passed). Auto-merge only
applies when checks are pending - you can merge directly." The session had
`CLAUDE.md`'s bullet resident ("a session merges only by arming auto-merge"),
reasoned that a direct merge of a clean head passes nothing the rule guards,
and merged through `merge_pull_request` as `fdc2531f`. `docs/maintainer.md`
already decided this case the other way - "the session tells you it cannot arm
it, and the Squash and merge is yours" (project owner, 2026-09-26, ratified,
over the session merging it directly through the API, `PL-V2X5`) - and nothing
a session reads before merging carries that sentence. No harm landed:
`fdc2531f`'s parent is `2193a222`, the base the tested head `43fdc0d4` already
held, and the two trees are identical. The next direct merge is not bounded
that way, because the race `PL-V2X5` names is between the read and the call.

**Two routes for triage to weigh.** One clause in `CLAUDE.md`'s merge bullet
carrying the exception, which the resident-set rule makes name what it
replaces; or a `PreToolUse` guard on `merge_pull_request` that refuses and
prints the exception, which fires whatever a session has read and needs no
resident text. The guard is the cheaper disposition by `CLAUDE.md`'s own
ordering, and is new machinery while `generator: live` items are open.
