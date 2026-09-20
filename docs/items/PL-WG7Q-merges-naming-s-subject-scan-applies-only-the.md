---
id: PL-WG7Q
title: _merges_naming's subject scan applies only the closed-here test and never the carried-work one, so a closure split from its work is recorded whenever its own subject leads with the id
priority: P2
effort: S
status: blocked
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
blocked-by: PL-GJPD
added: 2026-09-19
payoff: closes the half of the pull-request-provenance guard that holds only when an unrelated later commit happens to exist
verify: grep -q 'def test_a_subject_scan_hit_is_held_to_carried_work' subprojects/docket/tests/test_vcs.py
---

**Problem.** _merges_naming's subject scan applies only the closed-here test and never the carried-work one, so a closure split from its work is recorded whenever its own subject leads with the id

**Found 2026-09-19 closing `PL-YFXG`**, while reading the two paths that
recover a closure's number.

`_merges_naming` in `subprojects/docket/src/docket/vcs.py` tries the subject
scan first and the file walk second. Only the file walk applies
`_carried_work`:

```python
    for identifier, (revision, number) in candidates.items():
        path = f"{items_dir}/{closures[identifier]}"
        if _closed_at(revision, path, path, root, run):
            found[identifier] = number
```

So the `PL-YDL6` guard - a closure that landed without its work names no pull
request - is enforced on one of the two paths. A closure commit split from its
work is recorded, without the guard, whenever its own subject leads with the
item's id and no newer subject does. `CLAUDE.md` requires every commit subject
to lead with an id, so that is the ordinary case rather than a contrived one;
what keeps the shape rare is `PL-D2GW`'s same-commit closure rule, not this
reading.

`PL-YTDN` fell through to the file walk only because a *newer* commit, `#713`,
also led with `PL-YTDN` and took the candidate slot, and `_closed_at` then
declined it. Had `#712` been the newest subject naming the item, the scan would
have answered `712` directly and `PL-YFXG` would never have been visible.

**What needs deciding.** Either the guard belongs on both paths, or it belongs
on neither and the asymmetry should be documented as deliberate - the scan's
own docstring says the hit "is put to the test `_number_closing` already uses
on the file", which is true of the closed-here test and not of the
carried-work one. This is the same reading `PL-GJPD` proposes replacing, so
sequence the two: answer `PL-GJPD` first and apply whatever it lands on to
both callers.

**Why it matters.** The `PL-YDL6` guard exists so that a closure commit which
landed without its work names no pull request: a `pr:` recovered from such a
commit points at the change that *marked* the item done rather than the one
that did it, which is the same false provenance `PL-GJPD` measures from the
other direction. Enforcing that guard on one of the two recovery paths and not
the other means whether it applies is decided by which path happens to answer
first - the subject scan wins whenever the newest commit naming the id is the
closure's own, which `CLAUDE.md`'s leading-id rule makes the common case.

`PL-YTDN` reached the guarded path only by accident: a *newer* commit, `#713`,
also led with its id and took the candidate slot, so `_closed_at` declined it
and the file walk ran. Had `#712` been the newest subject naming the item, the
scan would have answered `712` with no guard applied and `PL-YFXG` would never
have been visible. A guard that holds only when an unrelated later commit
happens to exist is not a guard.

**Sequenced behind `PL-GJPD` rather than merged into it** (triage,
2026-09-20). Both items are about what evidence proves a commit carried an
item's work, and `PL-GJPD` proposes replacing that evidence wholesale - reading
the diff against the item's own `touches` instead of asking whether it left
`docs/items/`. Answering this one first would decide the reading twice. The
`blocked-by` records that order; the work here is to apply whatever `PL-GJPD`
lands on to both callers, or to document the asymmetry as deliberate if it
lands on keeping it.
