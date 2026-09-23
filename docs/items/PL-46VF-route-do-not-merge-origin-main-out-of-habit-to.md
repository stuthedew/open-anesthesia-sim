---
id: PL-46VF
title: Route 'do not merge origin/main out of habit' to a PreToolUse hook, the way no-prune-guard already does for prune
priority: P2
effort: M
status: dropped
classes: session-cost, infra
feature: dev-tooling
touches: .claude/hooks/no-habit-merge-guard.sh, .claude/settings.json, CLAUDE.md, docket.toml, tests/unit/test_no_habit_merge_guard.py
added: 2026-09-16
closed: 2026-09-23
reason: Superseded by PL-6MW8: with main requiring up-to-date branches, the base-merge rule became conditional on GitHub state (review, auto-merge, CI) that no read of the repository answers, and a merge ahead of a push being made anyway is now allowed, so a PreToolUse deny on the command string would refuse correct merges
verify: grep -q 'no-habit-merge-guard' .claude/settings.json && test -f tests/unit/test_no_habit_merge_guard.py && uv run pytest tests/unit/test_no_prune_guard.py
---

**Problem.** `CLAUDE.md` § "The queue" spends 11 resident lines on "Do not
merge `origin/main` into an open pull request out of habit" — a prohibition on
a command string, which is the exact shape `.claude/hooks/no-prune-guard.sh`
already handles for `git remote prune` as a `PreToolUse` deny on `Bash`.

`docs/resident-instructions.md` § "What was routed out" records the prune
routing and states the principle: "A prohibition on a command string is
decidable by reading the command. The prose fired when a session remembered it;
the hook fires always, and its deny message carries the recipe the caller
actually wanted."

**Why this one is harder than prune, and why it is still worth doing.** The
rule is conditional, not absolute: merging the base in is correct when the
branch is genuinely conflicted, or when a base-recovery notice has arrived. A
blanket deny would be wrong. But both exceptions are decidable from the
repository — `git merge-base --is-ancestor` and a merge dry-run answer the
first — so the hook can deny only the unconditional case and print the two
conditions under which the caller should proceed, which is more than the prose
does.

**The retirement test.** `docs/resident-instructions.md` § "When a resident
rule is retired" requires the carrier to be observed firing before the prose is
removed, and forbids removing a rule whose other triggers have no carrier. If
the hook cannot decide the base-recovery case, the resident bullet stays and
the hook is an addition rather than a routing — still worth it, but the item
closes without the reduction.

**Why it matters.** Eleven resident lines are spent on a prohibition over a
command string, which is the cheapest thing to route into a hook and the most
expensive thing to leave in prose: prose fires when a session remembers it, a
hook fires always. What forgetting costs is concrete - a merge commit pushed to
the head branch is a `synchronize` like any other, so it re-runs the whole of
`quality.yml` and discards a green result the branch had already earned, on
content `main`'s own run proved minutes earlier (`PL-WC72`).

**Done when.** A `PreToolUse` deny on the unconditional case exists, registered
in `.claude/settings.json` with a test of its own, and its message prints the two
conditions under which bringing the base in is correct - a genuine conflict, and
a base-recovery notice. Then either `CLAUDE.md`'s bullet is reduced to what the
hook cannot decide, or this item records - on `docs/resident-instructions.md`
§ "When a resident rule is retired" - that the base-recovery case is not
decidable from the repository and the bullet stays, the hook being an addition
rather than a routing.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** The hook does not exist, is not
registered in `.claude/settings.json`, and has no test; the precedent
(`no-prune-guard.sh`, a `PreToolUse` deny on `Bash`) and the routing record in
`docs/resident-instructions.md:41-45` both stand. Two small drifts: the
resident bullet is **10** lines (`CLAUDE.md:473-482`), not eleven, and its
enclosing heading is § "The queue, and how the project owner works".

**Dropped 2026-09-23 under `PL-6MW8`: the rule this would route was reversed.**
`main` now requires a branch to be up to date before it merges (project owner,
2026-09-23, ratified, on `PL-Z0SM`'s third-instance trigger), so `CLAUDE.md`'s
bullet no longer forbids bringing the base in. It says when: once, when
`behind` is the only thing stopping the merge, plus the two old cases and a push
being made anyway. That leaves nothing for a `PreToolUse` deny to decide.
Whether the pull request is waiting on review, armed for auto-merge, or green is
GitHub state, not repository state, and no read of the tree answers it. And a
local `git merge origin/main` ahead of a push the session is making anyway is
now allowed, so a deny on the command string would refuse correct merges. The
wasteful case left, bringing the base in while the pull request waits on
review, can be done server-side with `update_pull_request_branch`,
which a `Bash` hook never sees.
