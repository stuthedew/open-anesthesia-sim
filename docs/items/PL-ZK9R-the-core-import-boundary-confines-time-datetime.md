---
id: PL-ZK9R
title: The core/ import boundary confines time, datetime and random but not secrets or uuid, which break the reproducibility guarantee by the same route
status: untriaged
added: 2026-09-05
---

**Problem.** The core/ import boundary confines time, datetime and random but not secrets or uuid, which break the reproducibility guarantee by the same route

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-J833` added three boundaries to
`tools/import_boundary_check.py` confining `time`, `datetime` and `random` out
of `src/anesthesia_sim/core/`, so that `docs/MODEL.md`'s "A run is a function
of its inputs and of the number of steps taken, and of nothing else" is
measured. Those are the three the brief named. They are not the only routes to
the same failure:

- `secrets` is a second RNG, seeded from the OS, and unlike `random` it cannot
  be made reproducible by passing a seed at all.
- `uuid.uuid4()` is `os.urandom` in a wrapper, and `uuid.uuid1()` is a clock
  *and* a MAC address.
- `os` cannot be confined — `os.path` is ordinary — but `os.urandom` and
  `os.times` reach the same places.
- `time` confines the stdlib module and says nothing about a third-party
  dependency that reads a clock internally.

**Why it matters, and why it is not urgent.** Nothing in `core/` imports any of
these today, and the three that are confined are overwhelmingly the ones a
compartment would reach for by accident, which is what the guard is against
(the tool's own docstring says it guards against an accident, not against
evasion). So this is a completeness question rather than a hole: the check is
correct about what it claims, and the claim is narrower than the guarantee.

**The decision.** Whether the boundary is meant to enumerate the packages a
compartment might plausibly reach for — in which case `secrets` and `uuid` are
two more table rows and the reasons are already written — or whether it is meant
to *state* the guarantee, in which case an enumeration is the wrong shape and
the question is what the right one is. The file's own docstring says which
packages ought to be confined is a person's judgment, deliberately not the
tool's, so this is the owner's call rather than a session's.

**Cost of the narrow answer.** Two `Boundary` entries with an empty `allowed`,
matching the three already there, and one parametrized test. Under an hour.

**Done when.** The queue records whether `secrets` and `uuid` join the table,
and if they do, they are in it with the reason beside each.
