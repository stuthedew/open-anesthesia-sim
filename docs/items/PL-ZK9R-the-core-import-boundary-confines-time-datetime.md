---
id: PL-ZK9R
title: The core/ import boundary confines time, datetime and random but not secrets or uuid, which break the reproducibility guarantee by the same route
priority: P2
effort: S
status: done
classes: infra, docs
feature: core-guard-coverage
milestone: v0.4.0
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, docs/ARCHITECTURE.md, docs/MODEL.md, README.md
added: 2026-09-05
closed: 2026-09-05
pr: 336
verify: uv run pytest tests/unit/test_import_boundary_check.py && grep -q 'secrets' tools/import_boundary_check.py
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

**Decided 2026-09-05 (project owner): yes, both join the table.** The boundary
enumerates the packages a compartment might plausibly reach for, and `secrets`
and `uuid` are two of them.

**Resolved 2026-09-05.** Two entries in `BOUNDARIES`, matching the three
`PL-J833` added: `src/anesthesia_sim/core`, an empty `allowed`, and the reason
beside each. Six boundaries declared, 29 modules read, and the two verified
against the real tree - `import secrets` and `import uuid` in `core/tissue.py`
exit 1 naming the file, the line and the reason.

**The reasons were verified against the stdlib rather than written from
memory** (CPython 3.14.7, the interpreter `src/` targets):

- `secrets._sysrand` is a `random.SystemRandom`, whose `seed()` docstring reads
  *Stub method. Not used for a system random number generator*; seeding it
  twice with the same value produces different draws, and `getstate()` raises
  `NotImplementedError: System entropy source does not have state`. So a run
  reaching `secrets` cannot be made reproducible by any means, where a seeded
  `random.Random` could be. That is why it is strictly worse than `random`.
- `uuid.uuid4()` is `int.from_bytes(os.urandom(16))` with the version flags
  applied - the unseedable generator again.
- `uuid.uuid1()` is documented as *a UUID from a host ID, sequence number, and
  the current time*, so it is the wall clock plus the host's hardware address,
  and it makes a run differ between machines as well as between runs.

**Scope held.** `os` was considered and rejected: `os.path` is ordinary and
confining the package would fail on imports the design needs, so `os.urandom`
and `os.times` remain reachable. That is a stated limit of an enumeration, not
an oversight - the tool's docstring already says the guard is against an
accident rather than against evasion. A third-party dependency reading a clock
internally is outside what an import boundary can see at all.

**Docs swept:** `README.md` (the tools paragraph's package list),
`docs/ARCHITECTURE.md` (the package-map comment and the paragraph on why the
two trees differ), `docs/MODEL.md` ("The reproducibility guarantee" now names
all five packages, cites both items, and calls out the two that seeding cannot
recover from).
