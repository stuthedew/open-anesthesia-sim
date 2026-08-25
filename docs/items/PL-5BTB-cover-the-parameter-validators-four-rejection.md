---
id: PL-5BTB
title: Cover the parameter validators' four rejection paths
priority: P2
effort: S
status: done
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_parameters.py
verify: uv run pytest --cov=anesthesia_sim.core.parameters --cov-fail-under=100
added: 2026-08-25
closed: 2026-08-25
commit: 486c3c4
---

**Problem.** Four rejection paths in `core/parameters.py` never execute under
the test suite. Line 117 raises `ValueError("must be a nonempty string")`;
line 124 raises `ValueError("schema_version must be an integer")`; line 136
raises `ValueError("must be a number")`; line 150 raises `ValueError("must not
exceed 1")`. Coverage confirms all four as unreached.

**Why it matters.** These are the guards that stop a malformed agent or
patient data file from loading and producing a plausible but wrong clinical
value. An untested guard is a guard nobody has confirmed fires — it can be
broken by a later refactor with the whole suite still green, which is
precisely the failure the guards exist to prevent.

**Where.** `src/anesthesia_sim/core/parameters.py`; the tests belong in
`tests/unit/test_parameters.py`.

**First step.** These are pydantic field validators, so the `ValueError`
raised inside them does not reach the caller as a `ValueError` — it surfaces
as `pydantic.ValidationError` with the message embedded. Assert on
`pydantic.ValidationError` and match the message text given above. Do not
assert `ValueError` and do not adjust the expectation to whatever is observed:
if the surfaced type or message disagrees with this brief, that is a finding
to capture, not a test to bend.

Line 124's function has two rejection branches — a non-integer
`schema_version` and an integer that is not `SUPPORTED_SCHEMA_VERSION`. Only
the first is uncovered, but cover both; a version-mismatch test that nobody
wrote is the more likely one to matter later.

**Scope.** Tests only. This item may not modify `core/parameters.py` or any
other file outside `touches`; the validators are the specification and are not
being changed. It is classed `test, infra` rather than `safety` on purpose:
the class describes the deliverable, which is a test file, not the subject
matter it exercises. Editing a validator would be safety work and a different
item.

**Correction to the `verify:` command (2026-08-25).** The command originally
written here was wrong in two ways, both found by a worker refusing to guess
at it rather than by anyone testing it first.

`--cov=` was given a file path. `pytest-cov` reads that as a module name, finds
nothing imported under it, and reports no data — the run then fails
`--cov-fail-under`, so it fails loudly rather than passing falsely, but it
proves nothing about the guards.

Scoping the run to this item's own test file also demanded more than the item
asks: lines covered by the rest of the suite show as uncovered when only one
test file runs, so `--cov-fail-under=100` could not be reached without writing
tests outside this item's scope.

The corrected command runs the whole suite with coverage scoped to the module,
which measures exactly what this item is responsible for.

**Done when.** The `verify:` command above passes and `make check` is green.

**Worked.** Nothing the brief did not specify.
