---
id: PL-HMZZ
title: Which pull request carried a closed item's work is inferred from commit history after the merge and never recorded when the merge happens - ten items, four open
priority: P2
effort: M
status: needs-decision
classes: defect
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
payoff: Which pull request carried an item becomes one recorded fact, so a new shape of history stops costing an item
root-cause-of: PL-2XTF, PL-GW37, PL-YDL6, PL-S5LB, PL-KX9N, PL-YFXG, PL-LPWK, PL-QNYF, PL-GJPD, PL-WG7Q
generator: live - closures_on_base still infers the carrying pull request from merge subjects and _number_closing after the merge, and four members are open (PL-LPWK, PL-QNYF, PL-GJPD, PL-WG7Q)
---

**Problem.** Which pull request carried a closed item's work is inferred from commit history after the merge and never recorded when the merge happens - ten items, four open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. It came up in the inflow
sweep and survived three skeptics. A second round asked whether `PL-XYQW`
(stored `pr:`) already covers it. All three skeptics said no: `PL-XYQW`'s
record and its spent verdict ("the cut ... writes pr: before the notes
render") cover the timing half, and this is the inference half.

**The mechanism.** Which pull request carried a closed item's work is never
recorded when the merge creates that fact. The merge-time write was removed
(`PL-N5WZ`, #265: a `GITHUB_TOKEN` push starts no workflow, which is in the
digest's dead ends). So `closures_on_base` (`vcs.py:4295`) infers it later,
from merge subjects (`_merges_naming`) and then `_number_closing`. Each new
shape of history misleads it: a queue-only closure, a triage pass that also
edited `ROADMAP.md`, a rider id that never leads a subject (`PL-GW37`).

**Members.** `PL-2XTF`, `PL-GW37`, `PL-YDL6`, `PL-S5LB`, `PL-KX9N` and
`PL-YFXG` (done); `PL-LPWK` (needs-decision), `PL-QNYF` and `PL-GJPD` (ready),
and `PL-WG7Q` (blocked) are open.

**Not the claim family.** The audit tested whether this is `PL-MB2W`'s record
(who holds an item), since both go through `vcs._annotates_only`. Three of
three skeptics refuted it: a shared function is not a shared record, and which
pull request landed an item is a fact the merge authors.

**Why it matters.** `pr:` is what `docket check` and the release notes attribute work by. Each misattribution is plausible-looking, and ten items in three weeks means inference keeps meeting new history shapes.

**Decision needed.** Where can the carrying pull request be recorded as a fact, given that a merge-time CI write cannot land? One option is the session that opened the pull request writing it on the branch before the merge. The other is keeping inference and closing this head spent. Recommendation: settle it inside `PL-LPWK`, which already holds the open design question.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Against this
decision it rules out keeping the inference and closing this head spent. The
durable shape is a pull request number written as a fact before the merge,
not recovered from history afterwards. One candidate, a lead rather than a
finding: the session writes `pr:` once the pull request exists, and the pull
request's own CI checks it, since CI knows its own number. Settle it inside
`PL-LPWK`. Reading the direction this way is this session's call, so ordinary
evidence reopens it.

**Done when.** The pull request that carried an item is recorded as a fact at
a point that can record it, and the readers use that record. Or the owner
decides inference stays, and this head is closed spent with that recorded.
`PL-LPWK` is the open design question closest to this, so read it first.
