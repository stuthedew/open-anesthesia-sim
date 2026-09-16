---
id: PL-SY1J
title: bin/docket show named only one of two branches carrying PL-D1RT, and it was the later one, so the session holding the item read a verdict telling it to stand down
status: untriaged
feature: inflight-verdict
added: 2026-09-16
---

**Problem.** bin/docket show named only one of two branches carrying PL-D1RT, and it was the later one, so the session holding the item read a verdict telling it to stand down

**Observed 2026-09-16, mechanism not determined.** Recorded as an instance
rather than a diagnosis; whoever takes this should reproduce it before
believing the framing below.

**What happened.** Two branches carried `PL-D1RT` (the stale `v0.5.x — the
interface pass` citations), each with a commit whose subject leads with the id:

| Branch | Commit | Committed |
| --- | --- | --- |
| `claude/exciting-dirac-q7iyez` (`#643`) | `0d5fac0` | 19:52:55Z |
| `claude/awesome-heisenberg-gp7ev6` (`#645`) | `0db05f1` | 20:01:37Z |

Both were pushed. Run from the first branch, after `git fetch origin`,
`bin/docket show PL-D1RT` printed one carrier and it was the **later** one:

> `IN FLIGHT on origin/claude/awesome-heisenberg-gp7ev6 (last commit today) -
> do not start PL-D1RT again.`

`bin/docket flight` agreed, listing one branch per item for all five it
reported.

**Why that is the wrong way round.** `.claude/skills/docket/SKILL.md` says the
command "prints the carriers in order - whichever commit named the item first
holds it", and that both sessions compute the same order from the same commits
so both read the same answer. Here the earlier committer was shown a verdict
naming only the later one, which reads as an instruction to stand down. The
skill names the cost of getting this wrong: "the outcome that costs most is not
both continuing, which is where the project already was, but **both standing
down**: the item is then unstarted and each session believes the other has it."

**What was ruled out.** There is no current-branch filter in
`subprojects/docket/src/docket/vcs.py` - `grep` for `symbolic-ref` and
`current_branch` across `subprojects/docket/src/docket/*.py` returns nothing -
so this is not a deliberate "exclude the branch you are on" rule. Whether
`branches_in_flight` reports one carrier per item by construction, or whether
this ref was excluded for some other reason, was **not** established.

**It did not cost anything this time**, which is why this is an item rather
than an interruption: the two sessions reached the same disposition
independently, and `#643` stood down to `#645` on the merits - `#645` also
re-points `PL-C4RS` and takes `main` green, which `#643` did not.

**Done when** the behaviour is reproduced, and either the command names every
carrier in first-commit order as the skill describes, or the skill is corrected
to say what the command actually reports.
