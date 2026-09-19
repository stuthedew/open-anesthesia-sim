---
id: PL-DN5K
title: Recover PL-050P and PL-NZC0 from origin/claude/magical-bohr-brjvi4, where both were dropped with reasons on a branch that has no pull request and nobody will merge
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
milestone: v0.4.28
touches: docs/items
added: 2026-09-19
closed: 2026-09-19
verify: grep -rq '^id: PL-NZC0$' docs/items/ && grep -rq '^id: PL-050P$' docs/items/
---

**Problem.** Recover PL-050P and PL-NZC0 from origin/claude/magical-bohr-brjvi4, where both were dropped with reasons on a branch that has no pull request and nobody will merge

**Observed 2026-09-19, after a fetch.** `bin/docket stranded` named both items as
existing only on `origin/claude/magical-bohr-brjvi4`. That branch's newest
commit is `PL-NZC0, PL-050P: drop the Projects trial items, declined`
(2026-09-19 04:12), and `mcp__github__list_pull_requests` shows one open pull
request in the repository - `#691`, this branch's - so nothing will merge it.
`origin/main` holds no copy of either file, so the recovery creates rather than
overwrites and the `PL-KBFN` hazard (a `git checkout` restoring an older copy
over a merged one) cannot arise here.

**What is stranded is the `reason`, which is the part that matters.** Both items
are `status: dropped`, so no work is lost - but the skill's rule is that the
file is never deleted, because the reason is what stops the finding being
re-raised. `PL-NZC0` records the project owner declining a Claude Code Projects
trial on 2026-09-19 and, explicitly, that it is a not-yet rather than a refusal
of the mechanism; `PL-050P` records that its overlap with `PL-BHVM`'s design
round is moot without such a trial, so that round should pick its route on this
repository's evidence alone. Left on the branch, both dispositions vanish and
the next session that reaches `PL-BHVM` re-derives them.

**Filed before the work, per `CLAUDE.md`'s housekeeping rule.** Recovering a
stranded item is repository work no item names, and every in-flight guard this
project has matches a `PL-` id, so unfiled it reads as nobody's to all of them.

**Done when.** Both files stand on the default branch with their front matter
and `reason` as the branch wrote them, `bin/docket check` is clean, and
`bin/docket stranded` no longer names either.
