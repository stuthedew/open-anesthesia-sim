---
id: PL-5BTB
title: Cover the parameter validators' four rejection paths
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_parameters.py
verify: uv run pytest tests/unit/test_parameters.py --cov=src/anesthesia_sim/core/parameters.py --cov-fail-under=100
added: 2026-08-25
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

**Done when.** The `verify:` command above passes and `make check` is green.
