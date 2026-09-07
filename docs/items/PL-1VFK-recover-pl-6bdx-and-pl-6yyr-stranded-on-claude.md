---
id: PL-1VFK
title: Recover PL-6BDX and PL-6YYR, stranded on claude/gate-items-8yep0k after its pull request merged without the two captures pushed behind it
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
milestone: v0.4.8
touches: docs/items
added: 2026-09-07
closed: 2026-09-07
pr: 437
verify: bin/docket check && bin/docket show PL-6BDX >/dev/null && bin/docket show PL-6YYR >/dev/null
---

**Problem.** Recover PL-6BDX and PL-6YYR, stranded on claude/gate-items-8yep0k after its pull request merged without the two captures pushed behind it


`claude/gate-items-8yep0k` opened its pull request as `#430` (`PL-T691`, the
run as its control-input timeline), which squash-merged at 16:46. Two captures
were pushed onto the branch **after** that merge, at 17:35 and 17:37, and
nothing merges a branch twice - so `e7ad44f4` and `e2a7ea7e` were the whole of
what the branch carried that `main` lacked, and both were items rather than
code.

The session that wrote them is archived, so this is the case
`.claude/skills/docket/SKILL.md` distinguishes by judgment rather than by
command: `bin/docket stranded` cannot tell a live branch from an abandoned one,
and here the branch's pull request has merged and its session has ended, so
nobody will merge it. Recovered on the project owner's approval, 2026-09-07.

**What was recovered, and why each still stands.**

- `PL-6BDX` - two shipped items still reported in flight because their branch
  refs outlived their merges. Live: this session's own start-up digest listed
  `PL-GVXP` and `PL-S5LB` as in flight, and both shipped, in v0.4.7 and v0.4.6
  respectively.
- `PL-6YYR` - a release tag can be pushed for a version that was never cut, and
  nothing detects it. The **instance** it names has since been cleared - the
  `v0.4.8` tag was deleted from `origin`, and `git ls-remote --tags origin`
  now stops at `v0.4.7` - but the **gap** it reports has not: `bin/docket
  release` refuses to cut while the previous release is untagged, and nothing
  guards the inverse at the moment somebody tags. A note recording that
  distinction is appended to the item, so a triage pass does not drop a live
  finding as already fixed.

Both come back `untriaged`, which is correct: recovering a file is not
triaging it, and `bin/docket triage` is what folds them into the queue.

**What this does not do.** The stale `origin/claude/gate-items-8yep0k` ref is
left in place. It now carries nothing the store lacks, so it is safe to drop -
but a branch deletion from a session is exactly the operation `PL-TFWR` records
as failing while looking as though it succeeded, and `PL-6BDX` is the item that
covers the class.
