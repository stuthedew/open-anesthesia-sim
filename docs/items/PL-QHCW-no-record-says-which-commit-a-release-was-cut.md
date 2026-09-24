---
id: PL-QHCW
title: No record says which commit a release was cut on: release.md hands the owner a tag placed by hand from a moving ref, and each reader then takes the tag for the cut - six items, three open
priority: P2
effort: M
status: needs-decision
classes: defect
touches: .claude/skills/docket/modes/release.md, subprojects/docket/src/docket/cli.py, tools/doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
payoff: The commit a release was cut on becomes a recorded fact, so the tag and its readers stop disagreeing
root-cause-of: PL-VYK1, PL-6YYR, PL-KFWL, PL-BKDP, PL-YKSD, PL-6SV4
generator: live - release.md:191 still hands the owner git tag -a from origin/main and cli.py:2694 prints an unfilled MERGE_COMMIT, so no record says which commit a cut was made on; three members are open
misread: Which commit a release was cut on, if it was cut at all
---

**Problem.** No record says which commit a release was cut on: release.md hands the owner a tag placed by hand from a moving ref, and each reader then takes the tag for the cut - six items, three open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. It came up in the inflow
sweep and survived three skeptics, and no recorded head covers it.

**The mechanism.** A release is recorded in the tree by the cut: the
`pyproject.toml` version, `docs/releases/` notes and the `ROADMAP.md` version
row. It is recorded outside the tree by a tag the owner pushes by hand. The
handover is `git tag -a v0.3.0 origin/main` (`.claude/skills/docket/modes/release.md:191`),
and `cli._hand_off` (`cli.py:2694`) prints an unfilled `MERGE_COMMIT`. So the
tag lands wherever `origin/main` has moved to by then. Each reader then takes
the tag for the cut:

- `_check_tag_versions` (`tools/doc_check.py:2891`) compares only the version
  at the tag.
- `cli._untagged_warning` (`cli.py:2827`) greps `Release vX.Y.Z`, which no
  v0.4 or v0.5 cut subject matches.

**Members.** `PL-VYK1`, `PL-6YYR` and `PL-KFWL` (open, ready); `PL-BKDP`,
`PL-YKSD` (done); `PL-6SV4` (dropped). `PL-6SV4` reproduced the state on
2026-09-23.

**Why it matters.** Every tag since v0.4 has been read against a cut it may not sit on, and a later commit that declares the same version passes `_check_tag_versions`. So a wrong tag is silent, and nothing but a person checking by hand catches it.

**Decision needed.** Record the cut commit when the cut merges (the squash sha, read back by the cut's own close-out), or keep the hand-placed tag and close this head spent? Recommendation: record it, because three members are open and every one re-derives the same missing fact.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Against this
decision it rules out keeping the hand-placed tag and closing this head spent.
The design round decides where the cut commit is recorded, then makes the tag
and every reader of it use that record. Reading the direction this way is this
session's call, so ordinary evidence reopens it.

**Done when.** The commit a release was cut on is recorded when the cut
merges, and the tag and its readers use it. Or the owner decides the hand-placed
tag stays, and this head is closed spent with that recorded. It is a design
question, and while an open item carries `generator: live` any new check waits.
