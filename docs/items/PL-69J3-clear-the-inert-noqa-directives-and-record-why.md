---
id: PL-69J3
title: Clear the inert `noqa` directives and record why the deliberate suppressions exist
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.2.8
touches: pyproject.toml, src/anesthesia_sim/app/simulation_view.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_store.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tools/migrate_from_punch_list.py, tests/unit/test_doc_check.py, tests/unit/test_parameters.py, tools/doc_check.py
added: 2026-08-25
closed: 2026-08-31
pr: 105
---

**Problem.** The tree carries eight `noqa` directives that suppress nothing,
and a set of deliberate lint exceptions that carry no reason. Reproduce with:

```
uv run ruff check --select RUF100 --output-format concise
uv run ruff check --select S603,S607,S311 --output-format concise
```

The cause of the first is uniform and is not what "stale suppression" usually
means. `[tool.ruff.lint] select = ["E", "F", "I", "UP", "B"]`, so `BLE`,
`SLF`, `RUF` and the `S` (bandit) family are not enabled at all. Every one of
the eight directives names a rule the project does not run - `BLE001` at
`app/simulation_view.py:958`, `:990`, `:1015`; `SLF001` at
`tests/unit/test_parameters.py:431`; `E402` at
`subprojects/docket/tools/migrate_from_punch_list.py:22-23` and at
`tools/doc_check.py:73`; `F401` at
`subprojects/docket/tests/test_release.py:113`. They are not suppressions of
problems since fixed; they were written against rules that were never turned
on.

**Re-measured 2026-08-30.** The list above is that run, and the count fell
from ten to eight for two offsetting reasons: PL-STNV retired
`tools/review-verification/`, taking three of the original sites (`BLE001` at
`verify_findings.py:83` and `:278`, `SLF001` at `:248`) with it, and one new
inert `E402` has since appeared at `tools/doc_check.py:73`. The line numbers
in the second half below were not refreshed and have drifted further - the two
`ruff` commands above are the source of truth for both halves, and the second
now reports 22 sites across more files than it names.

The second command finds the converse: deliberate exceptions with no marker,
because the rule that would demand one is not enabled. `docket/vcs.py:52-53`
runs `git` from `PATH` (S603/S607), which is intended - every failure mode
there collapses to "nothing known about branches" so a checkout without git
still works - and `tools/doc_check.py:578` with its test at
`tests/unit/test_doc_check.py:307` does the same thing for the same reason.
`subprojects/docket/tests/test_store.py:50-58` constructs a seeded
`random.Random` (S311) so id allocation is deterministic under test.

**Why it matters.** Both halves mislead a later reader in opposite directions.
An inert `noqa` claims a rule is being suppressed when it is not, so anyone
reasoning about what the gate enforces reads the file wrong; and a deliberate
`subprocess` or `random` call with no recorded reason is exactly the shape a
later pass "fixes" - pinning an absolute path to `git`, or swapping the seeded
generator - breaking the thing the code was written to do. Low urgency: none
of it affects a shipped clinical value, and `make check` is green either way.

**Where.** `pyproject.toml` (`[tool.ruff.lint] select`) and the sites listed
above.

**Not a finding.** An earlier audit recorded `subprojects/docket/src/docket/store.py`
as tripping S311 because `new_id` type-hints `rng: random.Random | None` while
defaulting to `random.SystemRandom()`. It does not: ruff flags direct
`random.*` calls, and `new_id` calls `source.choice(...)` on a local. The
annotation being wider than the default is deliberate - the tests pass a
seeded generator through it - and needs no suppression. Recorded here so the
finding is not re-raised.

**Approach.** Reasons belong in prose comments, not in `noqa` directives for
rules the project does not enable - a `noqa` for a non-enabled rule is what
created this item, so adding more would reproduce it. So: delete all ten
inert directives (`uv run ruff check --select RUF100 --fix` does it), keep and
where necessary extend the plain comments that explain the deliberate cases,
and add one-line comments at the `git`-from-`PATH` and seeded-`Random` sites
saying why they are as they are. Widening `select` to enable `BLE`/`SLF`/`S`
is a separate question with its own cost - do not fold it in here.

**Done when.** `uv run ruff check --select RUF100` is clean, every deliberate
`subprocess` and seeded-random site named above carries a comment giving its
reason, and `make check` still passes.
