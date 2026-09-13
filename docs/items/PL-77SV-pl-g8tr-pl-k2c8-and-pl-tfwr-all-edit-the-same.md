---
id: PL-77SV
title: PL-G8TR, PL-K2C8 and PL-TFWR all edit the same ten lines of the docket skill's recovery block, and PL-G8TR's Done-when is defined against that block's shape, so whoever lands first silently sets the other two's tests
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: docs/items/PL-G8TR-no-prune-guard-is-evaded-by-the-form-it.md, docs/items/PL-K2C8-the-docket-skill-s-stranded-branch-recovery.md, docs/items/PL-TFWR-a-session-cannot-delete-a-remote-branch-the-git.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -q '^blocked-by: PL-' docs/items/PL-K2C8-the-docket-skill-s-stranded-branch-recovery.md
---

**Problem.** PL-G8TR, PL-K2C8 and PL-TFWR all edit the same ten lines of the docket skill's recovery block, and PL-G8TR's Done-when is defined against that block's shape, so whoever lands first silently sets the other two's tests

**Confirmed at triage, 2026-09-12.** All three are open at `ready`, all three
declare `.claude/skills/docket/SKILL.md` in `touches`, and all three rewrite the
same recovery block - `PL-G8TR` (the no-prune guard is evaded by the form it
prints), `PL-K2C8` (the recovery deletes only the local tracking ref) and
`PL-TFWR` (a session cannot delete a remote branch). None of them declares a
`blocked-by` edge, so `bin/docket next` will offer any of the three to any
session, and `bin/docket concurrent` reports them only as sharing a file, which
the skill correctly says is a sequencing note rather than a refusal.

**Why it matters.** Sharing a file is the ordinary case and resolves at the
merge. This is the other one: `PL-G8TR`'s Done-when is written against the
block's *current* shape, so whichever of the three lands first does not merely
conflict with the other two - it silently redefines what proves them done, and
the redefinition arrives inside a resolved merge conflict where nobody is looking
for it. A session that resolves the conflict correctly, line by line, still ends
up satisfying a test that no longer means what it said.

**Done when.** The three carry an explicit landing order in the store rather
than in prose - the first to land declares nothing, the other two declare
`blocked-by` on it - and `PL-G8TR`'s Done-when is restated so that it names the
behavior it wants rather than the shape of the block it expects to find.
