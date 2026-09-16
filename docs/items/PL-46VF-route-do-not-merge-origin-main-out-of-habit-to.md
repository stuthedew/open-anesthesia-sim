---
id: PL-46VF
title: Route 'do not merge origin/main out of habit' to a PreToolUse hook, the way no-prune-guard already does for prune
status: untriaged
added: 2026-09-16
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
