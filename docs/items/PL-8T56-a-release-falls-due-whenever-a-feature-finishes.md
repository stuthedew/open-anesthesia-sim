---
id: PL-8T56
title: A release falls due whenever a feature finishes, but nothing raises it at the moment one does: v0.5.29 was cut only after the owner asked, with 16 features finished and 59 items unreleased since v0.5.28 that morning, because the merge that finishes a feature prints nothing and the Projects coordinator waits for a free code place to start the cut
priority: P3
effort: S
status: needs-decision
classes: infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests, .claude/skills/docket/modes/close-out.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
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
