---
id: PL-P909
title: A blocked item may outrank its blocker, and the blocked exemption lets a live safety defect sit outside the top band
priority: P1
effort: S
classes: safety, infra
status: done
feature: dev-tooling
touches: subprojects/docket
added: 2026-09-02
closed: 2026-09-02
commit: 92a8e55
pr: 220
---

**Problem.** `PL-YHF1` let a blocked item sit outside the top band despite a
`safety` class, which is right for work whose concern does not exist yet. It
did not distinguish that from the opposite case: a defect that is live **now**
and merely sequenced behind something else. Two gaps let that second case go
quiet:

1. **The exemption was inferred, not claimed.** It read the *absence* of a
   `defect` class as "anticipated", so forgetting to write one bought the
   exemption. The safe default was the one an omission could not reach.
2. **Nothing refused a priority inversion.** A P1 blocked by a P3 passed every
   rule. `bin/docket next` skips blocked items, so such an item is waiting on
   work ranked below fifty others, and its own band is a promise the blocker
   does not keep.

**Why it matters.** Together those are a hiding place for exactly the work
this queue is most careful about. An item can be classed `safety`, sit at P3,
be invisible to `next`, and be blocked by something nobody will pick — while
every check passes. The project owner asked the question that found it:
how does this tell anticipated safety work for a future feature apart from a
safety issue live in the wild that happens to be blocked by lower-priority
work?

**Where.** `subprojects/docket/src/docket/checks.py`, the safety band rule and
the new `_outranks_its_blocker`; `subprojects/docket/tests/test_checks.py`.

**Fixed, in two parts.**

- **The exemption is claimed and fails closed.** `anticipated` must be present
  on a blocked item for it to leave the top band. Absence, omission, or a
  misspelling all leave the strict rule in force, and the error tells the
  reader how to claim it. Whether a concern is live is a judgment a script
  must not make, so the check does not infer it — it refuses to proceed
  without an answer, which is the automatable half. This also means
  `PL-MVC2` (no declared class vocabulary) does not guard this rule: a typo
  here fails safe rather than escaping the pin.
- **A blocked item may not outrank its blocker.** The error names the fix as
  the blocker's — raise it — rather than offering the choice, because on a
  safety item the other direction is the re-classing this checker exists to
  prevent. Only open blockers are compared: a closed one holds nothing up,
  and a done item's priority is often cleared outright.

Six tests cover both parts, including the two negative cases that matter — a
misspelled `anticipated` and a blocked `safety, defect` — and the store
validates clean, with no existing inversion among its four blocked items.

**Done when.** A blocked safety item must claim `anticipated` to leave the top
band, a misspelling of it fails closed, an item may not rank above open work
it waits on, and each has a test.
