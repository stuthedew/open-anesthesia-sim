---
id: PL-GYRX
title: PL-C97K is a defect in the generator machinery but carries no impairs-generators: field, because it was in flight on another branch when the field was built - it ranks on its band alone until the field is added
priority: P3
effort: S
status: ready
classes: infra
feature: generator-machinery-rank
touches: docs/items
added: 2026-09-19
verify: grep -q 'impairs-generators:' docs/items/PL-C97K-docket-show-on-a-member-prints-nothing-about.md
---

**Problem.** PL-C97K is a defect in the generator machinery but carries no impairs-generators: field, because it was in flight on another branch when the field was built - it ranks on its band alone until the field is added

**Where.** `docs/items/PL-C97K-docket-show-on-a-member-prints-nothing-about.md`.
One line of front matter:

    bin/docket set PL-C97K --impairs-generators "docket show prints no reverse edge, so a session opening a member by name works it as an ordinary item while a generator above it is still being scoped"

**Why it was not done in PL-G5ZH's session.** `PL-C97K` was in flight on
`origin/claude/nifty-cannon-8rbkkt` while the field was being built. Its
close-out rewrites `status`, `closed`, `commit` and `pr` in the same front
matter, and the project's own guard says not to edit an item another branch is
carrying. The demonstration was run against the real store with the field
applied and reverted: `PL-C97K` ranked first, above both open `P1`s, on the
same tier as the generator `PL-HWW1`.

**Why it matters.** Nothing today - and that is the reason it needs recording
rather than doing. While the item is in flight `docket next` excludes it, so
the tier changes nothing about what is offered. The moment that branch merges
or is abandoned the field is the difference between `P2` and the generator
tier, and by then nobody will remember that it was owed.

**Done when.** `PL-C97K` carries `impairs-generators:`, `bin/docket check`
reports no error against it, and `bin/docket show PL-C97K` prints "ranked on
the generator tier". Do it after that branch has merged, not before.
