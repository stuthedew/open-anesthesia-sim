---
id: PL-WG7Q
title: _merges_naming's subject scan applies only the closed-here test and never the carried-work one, so a closure split from its work is recorded whenever its own subject leads with the id
status: untriaged
feature: commit-provenance
added: 2026-09-19
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
