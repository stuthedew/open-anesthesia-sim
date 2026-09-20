---
id: PL-SY1J
title: bin/docket show named only one of two branches carrying PL-D1RT, and it was the later one, so the session holding the item read a verdict telling it to stand down
priority: P2
effort: M
status: ready
classes: defect
feature: inflight-verdict
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, .claude/skills/docket/SKILL.md
added: 2026-09-16
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_every_carrier_of_an_item_is_named_in_first_commit_order' subprojects/docket/tests/test_vcs.py
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

**Why it matters.** The in-flight verdict's whole value is that both sessions
compute the same order from the same commits and therefore read the same answer.
If it names one carrier and that carrier is the later one, the session holding
the item is told to stand down - and the skill names the outcome that costs most:
not both continuing, which is where the project already was, but **both standing
down**, leaving the item unstarted with each session believing the other has it.
It cost nothing on 2026-09-16 only because the two sessions reached the same
disposition on the merits.

**Reproduce before believing the framing.** The brief records an observation, not
a diagnosis: a current-branch filter was ruled out, and whether
`branches_in_flight` reports one carrier per item by construction was not
established.

**Done when** the behaviour is reproduced in a test, and either `bin/docket show`
names every carrier in first-commit order as `.claude/skills/docket/SKILL.md`
describes, or that passage is corrected to say what the command actually
reports - the two documents agreeing being the property that matters, since a
session acts on the skill's description of the verdict rather than on the code.

**Re-pointed by `PL-BHVM`'s design round, 2026-09-19.** Question 1 — what a
silence means. The brief asks whoever takes this to reproduce before believing
its framing, and the round supplies a mechanism worth testing first: `precedence`
returns `carriers=()` **and** `unreadable=()` when its evidence fails, so a read
that could not see a carrier is indistinguishable from one that saw none. That
is the same defect as `PL-Q9Z1` reaching the verdict this item is about. Take
`PL-Q9Z1` first; this may resolve against it.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken: the mechanism
landed, the reproduction did not.** `PL-Q9Z1` closed 2026-09-19 (#687) and
gives `precedence` the failure channel this item guessed at -
`Precedence.declined` at `vcs.py:2327`, set from the runner's reason, and
`render.py:903-906` now prints "(This ordering is partial - … - so the other
session may be computing a different one. Do not stand down on it.)".
`test_vcs_silence.py:280-281` holds `precedence` to it.

Both disjuncts of the `Done when`'s second clause are also already satisfied,
and were before this item was filed: `render.py:886-890` names every carrier in
first-commit order, four tests in `test_vcs.py` (`:3509`, `:3517`, `:3596`,
`:3643`) pin that ordering, and `.claude/skills/docket/modes/start.md` §
"Mode: start an item" describes it correctly - all from `4c429e8` on 2026-09-04, twelve days before
the 2026-09-16 observation. So is the open question about
`branches_in_flight`: `vcs.py:2388` says it reports one branch per item
"deliberately", same commit.

**What is left is only the first clause: reproduce the behaviour.** Whether the
2026-09-16 observation had a cause beyond the silence is undiagnosed, and it
may not be settleable - the session's branch `claude/exciting-dirac-q7iyez` is
gone and that repository state cannot be reconstructed, so which of
`_head_carries` or a silenced `diff` dropped the claim cannot be distinguished
from here. If it cannot be reproduced, say so and close it rather than leaving
it open against a state nobody can rebuild.
