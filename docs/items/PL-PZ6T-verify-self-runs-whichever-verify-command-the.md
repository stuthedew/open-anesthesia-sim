---
id: PL-PZ6T
title: verify --self runs whichever verify: command the branch holds, so a close-out can replace a failing commissioned command with a weaker passing one and ACCEPT; the only trace is the front-matter NOTE every close-out prints, the one PL-KSV2 found readers skim
priority: P2
effort: S
status: blocked
classes: defect
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
blocked-by: PL-B8HZ
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
payoff: a close-out that rewrites the command proving its work can no longer turn that command's failure into ACCEPT
---

**Problem.** verify --self runs whichever verify: command the branch holds, so a close-out can replace a failing commissioned command with a weaker passing one and ACCEPT; the only trace is the front-matter NOTE every close-out prints, the one PL-KSV2 found readers skim

**Premise re-checked at triage, 2026-09-24, from the code rather than a
replay.** In `subprojects/docket/src/docket/verify.py`, the base's command
(`Commission.verify`, read by `commissioned_falsification`) is consulted only where the branch
also records a `not-delegable:` reason, which is the `PL-KSV2` guard. The
command the audit then runs is `item.verify`, the branch's own copy.

**Why it matters.** `ACCEPT` is the verdict a reviewer merges on. Where the
branch rewrote the command that proves the work, that verdict says only that
the branch's own test passes. This is `CLAUDE.md`'s first compounding test, a
check passing while its guarantee is void. It is already ranked, through its
head.

**Blocked on `PL-B8HZ`**, the live head that names this item in its
`root-cause-of:`. That head's design round sets one rule for which copy each
contract field is read from. The owner's direction of 2026-09-23 was "I'd
rather fix it right once, then fix it twice", recorded there. So fixing this
field on its own would be the per-field choice that direction rules out. When
the rule lands, this item is either done by it or becomes the small change that
applies it to `verify:`.

**Generator check.** A re-entry of `PL-KSV2` (closed 2026-09-23) at a
sibling site. `PL-KSV2` stopped a close-out that *deletes* its failing
`verify:`, and this is one that *replaces* it. The shared fact is that `verify
--self` runs the command from the branch under audit, although `falsifies:` is
read from the base's copy of the item. One instance, so there is no cluster.
