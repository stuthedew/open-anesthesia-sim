---
id: PL-ZMGR
title: A needs-decision item whose answer is 'retire this' can never carry falsifies:, because the field must predate the branch and the decision is the work, so every session-decided retirement REJECTs its own close-out
status: untriaged
feature: verify-replay-cost
added: 2026-09-19
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

**Not the same as `PL-7TYC`**, which fixed the matcher's substring greed. The
matcher is correct here; every line it named really is a removed assertion.

**Where the repair might go**, none of these yet chosen:

- Let a `needs-decision` item's *closure* declare `falsifies:` in the same
  commit that records the decision, on the grounds that the decision record and
  the field are the same act — and that `docket check` already holds the
  closure's other fields to the store's rules.
- Add the assertion check to the four `--self` relaxes, reported as `NOTE`
  with every line named. Weaker: it would stop refusing a real coverage loss on
  any self-audited branch, which is most of them.
- Leave it, and let each such close-out report the `REJECT` to the owner in
  the check's own words. That is what `PL-G6J5` did, and it costs a reader's
  attention every time while proving nothing.

The first is the narrowest and is the one to cost first.

**Done when** a session-decided retirement can reach `ACCEPT` without weakening
what the assertion check refuses on delegated work, or this item records why it
must keep reporting `REJECT`.
