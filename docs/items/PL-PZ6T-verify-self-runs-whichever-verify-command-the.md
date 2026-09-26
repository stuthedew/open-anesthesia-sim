---
id: PL-PZ6T
title: verify --self runs whichever verify: command the branch holds, so a close-out can replace a failing commissioned command with a weaker passing one and ACCEPT; the only trace is the front-matter NOTE every close-out prints, the one PL-KSV2 found readers skim
priority: P2
effort: S
status: done
classes: defect
feature: verify-close-out
milestone: v0.5.12
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
closed: 2026-09-25
pr: 1017
payoff: a close-out that rewrites the command proving its work can no longer turn that command's failure into ACCEPT
verify: grep -q 'def test_a_rewritten_command_prints_the_commissioned_one_beside_it' subprojects/docket/tests/test_verify.py
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

[superseded 2026-09-25] **Blocked on `PL-B8HZ`**, the live head that names this item in its
`root-cause-of:`. That head's design round sets one rule for which copy each
contract field is read from. The owner's direction of 2026-09-23 was "I'd
rather fix it right once, then fix it twice", recorded there. So fixing this
field on its own would be the per-field choice that direction rules out. When
the rule lands, this item is either done by it or becomes the small change that
applies it to `verify:`.

**Done when.** Where the base commissions a command and this branch's differs,
`verify --self` runs both: the branch's decides the check, and the commissioned
command and its exit are printed under it as a correction, so a rewritten
command can no longer turn its predecessor's failure into a silent `ACCEPT`.

**Generator check.** A re-entry of `PL-KSV2` (closed 2026-09-23) at a
sibling site. `PL-KSV2` stopped a close-out that *deletes* its failing
`verify:`, and this is one that *replaces* it. The shared fact is that `verify
--self` runs the command from the branch under audit, although `falsifies:` is
read from the base's copy of the item. One instance, so there is no cluster.

## Folded into PL-B8HZ's design round, 2026-09-25

Under the rule recommended there (`PL-B8HZ` § "Design round, 2026-09-25"),
`verify:` is a prediction the branch may correct: where the base commissions a
command and the branch's differs, both run, the branch's decides the check, and
the base's command and its exit are printed under it as a correction. This
item's shape - a failing commissioned command replaced by a weaker passing one -
then reaches `ACCEPT` only with "commissioned: `A` - fails on this tree; this
branch runs `B` instead" on the report, the trace the front-matter NOTE never
gave. Counted before choosing print over refuse: 163 of 1,437 close-outs on
`main` rewrote a commissioned command, and none was this shape, so a refusal
would have fired 163 times on correct work and caught nothing. Closes with the
head's build; `blocked` stands until then.

**Ratified with the head, 2026-09-25** (project owner, 2026-09-25, ratified,
over running the base's command as the measure and refusing where it fails):
this item closes with `PL-B8HZ`'s build.

## Closed by PL-B8HZ's build, 2026-09-25

`verify --self` now runs the commissioned command beside a differing branch
command and prints its exit under the check, so this item's shape reaches
`ACCEPT` only with ``commissioned: `A` - fails on this tree (exit 1); this
branch runs `B` instead`` on the report. Pinned by
`test_a_rewritten_command_prints_the_commissioned_one_beside_it` in
`subprojects/docket/tests/test_verify.py`, in both audit modes and for a
commissioned command that still passes as well as one that fails.
