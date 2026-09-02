---
id: PL-B32L
title: core/parameters.py raises OSError and JSONDecodeError outside the exception hierarchy its own docstring promises
status: needs-decision
priority: P2
effort: S
classes: defect
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
added: 2026-09-02
---

**Problem.** `_load_packaged_json()` calls `resource.open()` and
`json.load()` unwrapped, so a missing or malformed data file raises `OSError`
or `json.JSONDecodeError` to the caller. The module docstring states the
opposite: "Every raise this module makes to a *caller* is a
`SimulationConfigurationError`, so `core/` presents one exception hierarchy
at its boundary."

**Why it matters.** The claim is load-bearing rather than decorative - every
caller that catches `AnesthesiaSimulationError` is relying on it, and
`PL-YK2V` is the place where that reliance shows. A stated invariant that is
false is worse than an unstated one, because the code downstream is written
against it.

Reachability today is low: the data files ship inside the package, so this
needs a corrupted install, a truncated bundle, or a filesystem error. It
stops being low if agent files ever arrive from outside the wheel, which
`ROADMAP.md` item 1's plugin direction implies.

**Where.** `src/anesthesia_sim/core/parameters.py`, `_load_packaged_json()`
and the docstring's boundary claim.

**Decision needed.** Whether to close the gap or narrow the claim:

1. Wrap the two calls in `except (OSError, json.JSONDecodeError)` re-raised
   as `SimulationConfigurationError`, preserving the cause. The docstring
   then becomes true as written.
2. Amend the docstring to say the boundary covers validation failures and
   not I/O, and let callers handle the two separately.

Option 1 keeps one boundary rather than two, and is the smaller diff. Not
agreed - recorded from an audit.

**Done when.** The decision is recorded, and if the code changes, a test
points the loader at an unreadable and at a malformed resource and asserts
the raised type.

**Measured 2026-09-02.** Confirmed as written. With
`core/parameters.py`'s `files` pointed at a directory holding no
`sevoflurane.json`, `load_agent_parameters("sevoflurane")` raises
`builtins.FileNotFoundError`; with the file present but holding `{ not json`
it raises `json.decoder.JSONDecodeError`. Neither is an
`AnesthesiaSimulationError` - asserted directly, `isinstance(...)` is
`False`. The module's stated boundary is false for both.
