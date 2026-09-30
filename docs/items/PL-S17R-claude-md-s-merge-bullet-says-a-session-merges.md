---
id: PL-S17R
title: CLAUDE.md's merge bullet says a session merges only by arming auto-merge and omits docs/maintainer.md's exception for a pull request already clean, where the Squash and merge is the owner's, while the GitHub tool's refusal says 'you can merge directly' - so a session told 'Merge' merged #1224 through the API against PL-V2X5's ratified decision
priority: P2
effort: S
status: done
classes: defect, infra
feature: review-hold
touches: .claude/hooks/direct-merge-guard.sh, .claude/settings.json, tests/unit/test_direct_merge_guard.py, docket.toml, docs/ARCHITECTURE.md, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-28
closed: 2026-09-30
pr: 1242
payoff: a session told to merge a pull request that is already green and current can no longer merge it through the API: the call is refused, and the owner is told the Squash and merge is theirs, as PL-V2X5 decided
verify: grep -qF '^mcp__.+__merge_pull_request$' .claude/settings.json && grep -qF 'the Squash and merge is theirs' .claude/hooks/direct-merge-guard.sh && grep -qF 'def test_the_matcher_reaches_the_merge_tool_and_nothing_else' tests/unit/test_direct_merge_guard.py && grep -qF 'direct-merge-guard.sh' docs/ARCHITECTURE.md && grep -qF 'direct-merge-guard.sh' docs/maintainer.md
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

**Reproduced 2026-09-30.** `grep -c merge_pull_request .claude/settings.json`
printed 0, so no hook reached the merge tool, and `grep -ci 'clean status\|Squash
and merge' CLAUDE.md` printed 0, while `docs/maintainer.md` carried the answer on
one line. `fdc2531f` is on `origin/main`.

**Why it matters.** A session told "Merge" on a pull request already green and
current meets GitHub's "you can merge directly" and nothing else at that moment,
and one has already taken it. Its merge is an admin's, which passes the
up-to-date rule `main` holds everyone else to, so the next one to land after
another merge and before its own call puts an untested combination on `main`:
the merge skew `PL-6MW8` made `main` refuse, and the outcome `PL-V2X5` was
decided to prevent.

**Route taken, 2026-09-30: the guard.** No open item carries `generator: live`
now (`PL-MT3R`, the last head marked so, is done), so the pause that held new
machinery no longer applies. The guard fires at the call whatever a session has
read, in a subagent as in the main session; a clause would be more of the
resident prose that was in front of the session that merged `#1224`, and would
pay the resident-set rule's price besides. `CLAUDE.md`'s "so a session merges
only by arming auto-merge" stays: the hook sees only the MCP merge tool, and the
sentence still covers `gh pr merge` or a REST call from Bash in a session that
has either, so `docs/resident-instructions.md`'s retirement test is not met.

**Done when.** A call to the GitHub server's merge tool is refused by a
`PreToolUse` hook whose reason names arming as a session's route and, for a pull
request already clean, the owner's Squash and merge as `PL-V2X5` decided; tests
pin the matcher's reach, the refusal's text and the fail-closed direction;
`docs/ARCHITECTURE.md` § "Wired hooks" lists the hook; and `docs/maintainer.md`'s
exception says a hook enforces it.

**Generator check.** One-off. The fact misread is whom GitHub's "you can merge
directly" addresses, which `PL-V2X5` answered in a document; this is the second
item on it and there is no third. `PL-WFFX` and `PL-Y1W0` say "merged directly"
of the owner's browser merges, not of a session's API call.
