---
id: PL-ZMGR
title: A needs-decision item whose answer is 'retire this' can never carry falsifies:, because the field must predate the branch and the decision is the work, so every session-decided retirement REJECTs its own close-out
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-false-reject
milestone: v0.5.0
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, .claude/skills/docket/modes/close-out.md
added: 2026-09-19
closed: 2026-09-20
pr: 798
verify: grep -q 'def test_a_needs_decision_closure_may_declare_what_it_falsifies' subprojects/docket/tests/test_verify.py
---

**Problem.** A needs-decision item whose answer is 'retire this' can never carry falsifies:, because the field must predate the branch and the decision is the work, so every session-decided retirement REJECTs its own close-out

**Found 2026-09-19** on `PL-G6J5`'s own close-out. That item asked whether an
advisory should be re-based on a different denominator *or retired*, and made a
count the decider. The count said retire, so the work deleted the advisory and
its tests — and `bin/docket verify --self PL-G6J5` printed

```text
FAIL  no existing assertion removed - 29 line(s)
        assert [command.identifier for command in report.slow] == ["PL-SLOW"]
        assert already_passing(root, items, workers=8).slow == ()
```

All 29 were assertions about the retired advisory, which is exactly what the
item sanctioned deleting. `make check` passed, the `verify:` command passed,
and every other guard passed. The close-out still reads `REJECT`.

**Why `falsifies:` cannot cover it.** The field is deliberately read from the
*base's* copy of the item, so that a reviewer writes it before the branch
exists — "the whole worth of the field is that a reviewer wrote it first"
(`.claude/skills/docket/SKILL.md`). That works when the commission already
knows what becomes untrue. It cannot work here: at filing time the item had two
possible answers, and which assertions become false depends on which one is
chosen. The choosing *is* the work, and it happens on the branch.

So the guard fires by construction on a whole class of correct close-outs:
every retirement a session decides rather than receives. That is the same shape
as the four commission checks `--self` already relaxes — guards that are right
about delegated work and wrong about work a session was commissioned to decide.

**Why it matters.** The guard fires by construction on a whole class of correct
close-outs — every retirement a session decides rather than receives — so its
`REJECT` carries no information about *this* branch. That is the shape
`CLAUDE.md` calls a check being routed around: a reader who learns that the
close-out audit rejects whenever an item's answer was "delete this" stops
reading the block, and the block is also where a real protected-path failure or
a genuine coverage loss is printed. It is the same reasoning that put the four
commission checks behind `--self` in the first place (`PL-69JZ`, `PL-7XTS`) —
guards that are right about delegated work and wrong about work a session was
commissioned to decide.

**Not the same as `PL-7TYC`**, which fixed the matcher's substring greed. The
matcher is correct here; every line it named really is a removed assertion.

## Decided 2026-09-19: the closure declares it

**A `needs-decision` item's closure may declare `falsifies:` in the same commit
that records the decision** (project owner, 2026-09-19, ratified), chosen over
adding the assertion check to the four guards `--self` already relaxes, and over
leaving every such close-out to report `REJECT` and be explained in prose.

**Why the field can be trusted here when the general rule is that it cannot.**
`commissioned_falsification` reads `falsifies:` from the *base's* copy precisely
so a reviewer writes it before the work — "one added beside the deletion it
excuses is the worker's own word for it". That holds for a `ready` item, whose
commission is settled before the branch opens. It does not hold for a
`needs-decision` item: the base's copy saying `status: needs-decision` *is* the
standing statement that the question is open and the answer is the session's to
make, and `.claude/skills/docket/SKILL.md` already treats such an item's
deliverable as the item file itself.

**The gate is the base's status, never the branch's**, and that is what stops
the exemption being self-granted. A session cannot set its own item to
`needs-decision` on its branch and walk through, because the status is read from
the same base copy the field is. A `ready` item is untouched, so a delegated
worker still cannot add `falsifies:` to excuse deleting tests — which is the
property the rejected second option would have given away on every self-audited
branch.

**Where it goes.** `commissioned_falsification` (`subprojects/docket/src/docket/verify.py:883`)
returns the base's declaration; the refusal it feeds is the `item.falsifies and
not declared` branch at `verify.py:1320`. The change is to let that branch
honour the working tree's declaration when the base's copy reads
`status: needs-decision` *and* this branch's diff closes the item — and to say
in the check's own words that it did, rather than folding silently.

**Worked instance: `PL-G6J5`** (#705, the slow-command advisory retired on a
count). Its close-out printed `FAIL no existing assertion removed - 29 line(s)`,
every line an assertion about the advisory the item had sanctioned retiring,
with `make check` green and every other guard passing. Under this rule it
declares the retired advisory's assertions and reaches `ACCEPT`.

**Done when** a session-decided retirement can reach `ACCEPT` without weakening
what the assertion check refuses on delegated work, or this item records why it
must keep reporting `REJECT`.

**Grouped as `feature: verify-false-reject`** (`PL-JKML`'s duplicate sweep,
2026-09-20, confirmed on independent refutation). This and `PL-BX1C` are the
same failure from two directions: `bin/docket verify` REJECTing a close-out
that is correct. `PL-BX1C` is a *dropped* item's stale `verify:` still being
run; this is a `needs-decision` item whose answer is "retire this" being unable
to carry `falsifies:` at all, because the field must predate the branch and the
decision *is* the work. Both leave a session reporting a REJECT on work nobody
can fix, which is what trains a reader to skim the block where a real
protected-path failure prints.

## Built 2026-09-20

`commissioned_falsification` now returns a `Commission` — the base's
`falsifies:`, the base's `status`, and why neither could be read — and
`self_declared_falsification` decides the one case in which the branch's own
declaration is honoured: the base's copy reads `status: needs-decision`, the
base declares nothing, and this branch's item is at a closed status. The fold
says so on its own page rather than happening quietly: the detail reads
`N declared falsified by this closure` and a line underneath names the base as
what let it be.

Four tests hold the gate from both sides. The granted case reproduces
`PL-G6J5`'s failure exactly against the unpatched module — `FAIL no existing
assertion removed - 1 line(s)` — and the three refusals are a `ready` base
closed with the identical declaration, a `needs-decision` item this branch
leaves open, and an item captured *and* closed on one branch, which is the only
route by which a session could otherwise write both halves of the gate itself.

`.claude/skills/docket/modes/close-out.md` carried the instruction not to do
this — "do not add the declaration to the item on this branch to clear it" —
so it is edited here and `touches` widened to name it. Without that edit the
mechanism is unreachable by the session it exists for.
