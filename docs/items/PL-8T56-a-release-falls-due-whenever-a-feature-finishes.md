---
id: PL-8T56
title: A release falls due whenever a feature finishes, but nothing raises it at the moment one does: v0.5.29 was cut only after the owner asked, with 16 features finished and 59 items unreleased since v0.5.28 that morning, because the merge that finishes a feature prints nothing and the Projects coordinator waits for a free code place to start the cut
priority: P3
effort: S
status: dropped
classes: infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests, .claude/skills/docket/modes/close-out.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
reason: The Projects coordinator's release check (owner's Yes, 2026-10-18 21:41Z) closed the gap: four releases were cut within 4.5 hours of it, and v0.5.33's cut started seven minutes after the merge that finished three features. Outside Projects the digest's Releasable line already raises it, and option (a) would speak before the merge.
---

**Problem.** A release falls due whenever a feature finishes, but nothing raises it at the moment one does: v0.5.29 was cut only after the owner asked, with 16 features finished and 59 items unreleased since v0.5.28 that morning, because the merge that finishes a feature prints nothing and the Projects coordinator waits for a free code place to start the cut

**Why it matters.** A finished feature that waits for a release is work a
reader of the released app cannot see. The session-start digest's
`Releasable:` line does report what is releasable, but only to a session that
starts later. The session that finishes the feature is the one with the owner's
attention, and nothing tells it.

**Generator check.** The fact misread is "a release is now due". The digest's
`Releasable:` line already reads it from the store. The gap is the moment it is
read, not a second reader that disagrees, and no head's `misread:` names it. So
it is a one-off.

**Decision needed.** Where to raise "this closure finishes a feature, so a
release is due". The options are: (a) `bin/docket set --status done` prints it
when the write completes a feature, so the closing session's closing block
carries it to the owner; (b) a step in the close-out mode file telling the
session to check `bin/docket feature`; (c) a CI comment on the merge that
finishes the feature.

**Recommendation:** (a). It is printed by code at the one write every closure
makes, so it cannot be skipped the way a prose step can. It needs no CI token
or workflow, which (c) does. The Projects coordinator's wait for a free code
place is outside this repository and is not changed by any option.

**Done when.** The chosen moment prints the feature name and the count of
unreleased items, and a test in `subprojects/docket/tests/` pins it.

**Decided 2026-10-19, in the workflow decision batch: dropped, and none of
the three options is built.** The recommendation above is
`[superseded 2026-10-19: the gap it answers was closed outside the
repository]`. This was decided in the round as an obvious call and not put to
the owner. Four facts settle it.

1. The cause this item names is the one it says no option changes. The
   Projects coordinator waited for a free code place before starting a cut.
   On 2026-10-18 at 21:41Z the owner answered "Yes" to a coordinator rule that
   ends the wait. On every merge report the coordinator reads
   `bin/docket status`, and when it reports features finished since the last
   tag and nobody holds the release train, it starts the cut in that turn,
   above the place cap. That rule lives in the project's instructions, not
   in this repository.
2. The rule works, measured from the tags on origin. Before it, v0.5.28 was
   tagged at 13:39Z and v0.5.29 waited until the owner asked, at 22:11Z.
   After it, v0.5.30 was tagged at 22:56Z, v0.5.31 at 01:19Z (2026-10-19) and
   v0.5.32 at 02:16Z. Then #1620 merged at 02:26Z and finished three
   features. `PL-WQJS`, the cut of v0.5.33, claimed the release train at
   02:33Z, seven minutes later.
3. Outside Projects, a release is already raised at the next session's
   start. The digest's `Releasable:` line names the finished features and
   ends with "Offer X before taking new work"
   (`subprojects/docket/src/docket/render.py`, `_release_advice`).
4. Option (a) would speak at the wrong moment. `bin/docket set --status done`
   runs on the closing branch, before its pull request merges, so it would
   call a release due before the feature is on `main`. It would also say
   nothing when two branches each close one of a feature's last two items,
   because each branch's store still shows the other item open. In a Projects
   thread it would add a line that repeats the coordinator's own cut. Option
   (b) is a prose step at the same wrong moment. Option (c) speaks at the
   right moment, the merge, but it would add a workflow that does what the
   coordinator's merge-report check already does.

**Reopen when** a release is found overdue while the coordinator's rule is in
force, or after the Projects trial ends and a session that finished a feature
was not followed by a release. In the second case, the merge (option c) is
the moment to build for, not the closure.
